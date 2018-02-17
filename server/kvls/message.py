""" Module responsible for parsing and storing
    information from the stdin and stdout between
    client and the server"""
import re
import json
from kvls.utils import EOL, CHARSET

class Message(object):
    """ Base class of the objects which handle messages
        of the language server protocol specification"""
    def __init__(self):
        self.length = 0
        self.message = None
        self.encoding = CHARSET

    def build(self):
        """ Build and return full content of the message """
        return 'Content-Length: {}{}Content-Type: ' \
               'application/vscode-jsonrpc; charset={}{}{}{}'. \
               format(self.length, EOL, self.encoding, EOL, EOL, self.message)

class NotificationMessage(Message):
    """ Class responsible for parsing and storing information
        for the notification message which will be
        send to the client"""

    def content(self, content, method):
        """ Parse content of the message from dictionary to json format """
        self.message = json.dumps({"jsonrpc": "2.0", "method": method, "params": content},
                                  separators=(',', ':'))
        self.length = len(self.message)

class ResponseMessage(Message):
    """ Class responsible for parsing and storing information
        for the response message which will be
        send to the client"""

    def content(self, content, success, request_id):
        """ Parse content of the message from dictionary to json format """
        message_content = {}
        if success:
            message_content = {"jsonrpc": "2.0", "id": request_id, "result": content}
        else:
            message_content = {"jsonrpc": "2.0", "id": request_id, "error": content}
        self.message = json.dumps(message_content, separators=(',', ':'))
        self.length = len(self.message)

class RequestMessage(Message):
    """ Class responsible for parsing and storing information
        received in the request/notification message from the client"""

    def content_length(self, line):
        """ Parse Content length header """
        match = re.match('Content-Length: ([0-9]*)', line)
        self.length = int(match.group(1))

    def content_type(self, line):
        """ Parse content type header"""
        match = re.match('Content-Type: .*charset=(.*)', line)
        if match is not None:
            self.encoding = match.group(1)
        return match

    def content(self, content):
        """ Parse content of the message from json to dictionary format """
        self.message = json.loads(content, encoding=self.encoding)

    # Parsing is successful. Current method can be used
    def request_id(self):
        """ Return id of the request """
        return self.message["id"]

    def method(self):
        """ Return method name """
        return self.message["method"]

    def jsonrpc(self):
        """ Return jsonrpc version """
        return self.message["jsonrpc"]

    def params(self):
        """ Return params included in request """
        return self.message["params"]

class ErrorCodes(object):
    """ The error constants in case a request fails """
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32099
    SERVER_ERROR_END = -32000
    SERVER_NOT_INITIALIZED = -32002
    UNKNOWN_ERROR_CODE = -32001
    REQUEST_CANCELLED = -32800
