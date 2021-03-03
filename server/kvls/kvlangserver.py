"""KvLang language server support for the language of Kivy.

Current module is responsible for handling requests, notification from client or response/
notification from server to client. Server work in stdin/stdout comunication using
specification included in version 3.x of the language server protocol.

"""
from __future__ import absolute_import
from kvls.message import RequestMessage, ResponseMessage, NotificationMessage, ErrorCodes,\
    MessageType, MessageUtils
from kvls.kvlint import KvLint
from kvls.document import TextDocumentItem, TextDocumentManager
from kvls.logger import Logger
from kvls.utils import CHARSET, CharsetException

class KvLangServer(object):
    """Class responsible for managing Language Server Procedures."""

    SHUTDOWN = 6
    RUNNING = 8
    EXIT_SUCCESS = 0
    EXIT_ERROR = 1
    OFF_LINE = 4

    def __init__(self, stdin, stdout):
        """Initialize KvLang server."""
        self.logger = Logger("KvLangDebug")
        self.reader = stdin
        self.writer = stdout
        self.server_status = self.OFF_LINE
        self.document_manager = TextDocumentManager()
        self.kvlint = KvLint()
        self.request_procedures = {"initialize": self.initialize,
                                   "textDocument/completion": self.completion,
                                   "completionItem/resolve": self.resolve,
                                   "shutdown": self.shutdown}
        self.notification_procedures = {"initialized": self.initialized,
                                        "textDocument/didSave": self.did_save,
                                        "textDocument/didOpen": self.did_open,
                                        "textDocument/didClose": self.did_close,
                                        "textDocument/didChange": self.did_change,
                                        "exit": self.exit}

    def send(self, message):
        """Send message to the client."""
        self.logger.log_message(message)
        self.writer.write(message.build())
        self.writer.flush()

    def handle(self, content):
        """Start hadling input from stdin."""
        content_length = MessageUtils.fetch_content_length(content)
        # Read new line or additional content
        content_type_or_eol = self.reader.readline()
        charset = MessageUtils.fetch_charset(content_type_or_eol)
        if charset:
            # Read also new line because charset was found in header
            if charset != CHARSET:
                raise CharsetException("KvLang support only utf-8 encoding. "
                                       "Content-Type encoding: {}".format(charset))
            self.reader.readline()

        message_content = MessageUtils.parse_content(self.reader.read(content_length))
        if MessageUtils.is_notification(message_content):
            notification = NotificationMessage()
            notification.assign_message_content(message_content)
            self.logger.log_message(notification)
            self.notification_procedures.get(notification.method,
                                             self.default_notification)(notification)
        else:
            request = RequestMessage()
            request.assign_message_content(message_content)
            self.logger.log_message(request)
            self.request_procedures.get(request.method, self.default_request)(request)

    def run(self):
        """Start server for processing input from stdin."""
        self.server_status = self.RUNNING
        while True:
            if self.server_status == self.EXIT_SUCCESS:
                return self.EXIT_SUCCESS
            elif self.server_status == self.EXIT_ERROR:
                return self.EXIT_ERROR
            else:
                line_with_content = self.reader.readline()
                self.handle(line_with_content)

    def initialize(self, request):
        """Handle Initialize Request."""
        message = ResponseMessage()
        message.content({'capabilities': {'textDocumentSync': {'openClose': True,
                                                               'change': 0,
                                                               'willSave': False,
                                                               'willSaveWaitUntil': False,
                                                               'save': {'includeText': True}},
                                          #TODO 'completionProvider': {'resolveProvider': True}
                                          }}, True, request.request_id)
        self.send(message)

    def initialized(self, _):
        """Handle Initialized Notification."""
        if self.kvlint.KIVY_IMPORTED is False:
            message = NotificationMessage()
            message.content({'type': MessageType.INFO, 'message': self.kvlint.KIVY_IMPORT_MSG},
                            'window/logMessage')
            self.send(message)

    def did_save(self, notification):
        """Handle DidSaveTextDocument Notification."""
        document = self.document_manager.get(notification.params["textDocument"]["uri"])
        document.text = notification.params["text"]
        diagnostic = self.kvlint.parse(document)
        message = NotificationMessage()
        message.content({'uri': document.uri, 'diagnostics': diagnostic},
                        'textDocument/publishDiagnostics')
        self.send(message)

    def did_change(self, notification):
        """Handle DidChangeTextDocument Notification."""
        pass

    def did_open(self, notification):
        """Handle DidOpenTextDocumentParams Notification."""
        document = TextDocumentItem(notification.params["textDocument"]["uri"],
                                    notification.params["textDocument"]["languageId"],
                                    notification.params["textDocument"]["text"])
        self.document_manager.add(document)
        diagnostic = self.kvlint.parse(document)
        message = NotificationMessage()
        message.content({'uri': document.uri, 'diagnostics': diagnostic},
                        'textDocument/publishDiagnostics')
        self.send(message)

    def did_close(self, notification):
        """Handle DidCloseTextDocumentParams Notification."""
        # Clear diagnostic
        self.document_manager.remove(notification.params["textDocument"]["uri"])
        message = NotificationMessage()
        message.content({'uri': notification.params["textDocument"]["uri"],
                         'diagnostics': []}, 'textDocument/publishDiagnostics')
        self.send(message)

    def completion(self, request):
        """Handle CompletionParams Request."""
        # TODO Add full support for textDocument/completion with test
        message = ResponseMessage()
        message.content({'isIncomplete': False, 'items': []}, True, request.request_id)
        self.send(message)

    def resolve(self, request):
        """Handle CompletionItem Request."""
        # TODO Add full support for completionItem/resolve with test
        message = ResponseMessage()
        message.content({'isIncomplete': False, 'items': []}, True, request.request_id)
        self.send(message)

    def default_request(self, request):
        """Handle unknown request method which do not exist in procedures."""
        self.logger.log(Logger.INFO, "Server do not support request with method='{}'". \
                        format(request.method))
        message = ResponseMessage()
        message.content({'code': ErrorCodes.METHOD_NOT_FOUND, 'message': 'Method not found'},
                        False, request.request_id)
        self.send(message)

    def default_notification(self, notification):
        """Handle unknown notification method which do not exist in procedures."""
        self.logger.log(Logger.INFO, "Server do not support notification with method='{}'". \
                        format(notification.method))

    def shutdown(self, request):
        """Handle Shutdown Request."""
        message = ResponseMessage()
        message.content({}, True, request.request_id)
        self.server_status = self.SHUTDOWN
        self.send(message)

    def exit(self, _):
        """Handle Exit Notification."""
        if self.server_status == self.SHUTDOWN:
            self.server_status = self.EXIT_SUCCESS
        else:
            self.server_status = self.EXIT_ERROR
        self.logger.log(Logger.INFO,
                        "Server exit with server_status={}".format(self.server_status))
