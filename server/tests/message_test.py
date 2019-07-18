"""Unit tests for Message module."""
from __future__ import absolute_import
import unittest
from kvls.message import NotificationMessage, ResponseMessage, RequestMessage, ErrorCodes, \
    MessageUtils, Message
from kvls.utils import EOL_LSP, CHARSET

class MessageTest(unittest.TestCase):
    """Message UnitTest."""

    def test_message_utils(self):
        """Test MessageUtils methods."""
        self.assertEqual(172, MessageUtils.fetch_content_length("Content-Length: 172"))
        self.assertEqual("utf-8", MessageUtils.fetch_charset("Content-Type: application/" \
                                                             "vscode-jsonrpc; charset=utf-8"))
        self.assertEqual(None, MessageUtils.fetch_charset(""))

        notification = MessageUtils.parse_content('{"jsonrpc":"2.0","method":'\
                                                  '"initialized","params":{}}', "utf-8")
        self.assertEqual(MessageUtils.is_notification(notification), True)

        request = MessageUtils.parse_content('{"jsonrpc":"2.0","id":0,"method":'\
                                             '"initialize","params":{}}', "utf-8")
        self.assertEqual(MessageUtils.is_notification(request), False)

    def test_message_base_class(self):
        """Test build method of the bas Message class."""
        message = Message()
        message.message_content = {"jsonrpc": "2.0", "method": "textDocument/publishDiagnostics",
                                   "params": {"uri":"path", "diagnostics":[]}}
        content_str = '{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics",'\
                      '"params":{"uri":"path","diagnostics":[]}}'
        expected = 'Content-Length: {}{}Content-Type: ' \
                   'application/vscode-jsonrpc; charset={}{}{}{}'. \
                   format(len(content_str), EOL_LSP, CHARSET, EOL_LSP, EOL_LSP, content_str)
        self.assertEqual(expected, message.build())

    def test_notification_message(self):
        """Test checking notification message methods."""
        message = NotificationMessage()
        message.content({'uri': "path_to_document",
                         'diagnostics': []}, 'textDocument/publishDiagnostics')
        self.assertEqual(message.jsonrpc, "2.0")
        self.assertEqual(message.method, "textDocument/publishDiagnostics")
        self.assertEqual(message.params["uri"], "path_to_document")
        self.assertEqual(message.params["diagnostics"], [])

        message.assign_message_content({"jsonrpc": "2.0",
                                        "method": "textDocument/publishDiagnostics", "params":
                                        {'uri': "path", 'diagnostics': [1]}})

        self.assertEqual(message.jsonrpc, "2.0")
        self.assertEqual(message.method, "textDocument/publishDiagnostics")
        self.assertEqual(message.params["uri"], "path")
        self.assertEqual(message.params["diagnostics"], [1])

    def test_response_message_success(self):
        """Test checking success response message methods."""
        request_id = 12
        message = ResponseMessage()
        message.content({"capabilities":{"textDocumentSync": {}}}, True, request_id)
        self.assertEqual(message.jsonrpc, "2.0")
        self.assertEqual(message.request_id, request_id)
        self.assertDictEqual(message.result["capabilities"], {"textDocumentSync": {}})

    def test_response_message_error(self):
        """Test checking error response message methods."""
        request_id = 14
        message = ResponseMessage()
        message.content({'code': ErrorCodes.METHOD_NOT_FOUND, 'message': 'Method not found'},
                        False, request_id)
        self.assertEqual(message.jsonrpc, "2.0")
        self.assertEqual(message.request_id, request_id)
        self.assertEqual(message.error["code"], ErrorCodes.METHOD_NOT_FOUND)
        self.assertEqual(message.error["message"], "Method not found")

    def test_request_message(self):
        """Test checking request message methods."""
        message = RequestMessage()
        request_id = 16
        message.assign_message_content({"jsonrpc": "2.0", "id": request_id,
                                        "method": "initialize", "params":
                                        {"processId": 1, "rootPath": "path.kv"}})
        self.assertEqual(message.jsonrpc, "2.0")
        self.assertEqual(message.request_id, request_id)
        self.assertEqual(message.method, "initialize")
        self.assertDictEqual(message.params, {"processId": 1, "rootPath": "path.kv"})
