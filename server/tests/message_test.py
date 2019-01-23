""" Unit tests for Message module """
from __future__ import absolute_import
import unittest
from kvls.message import NotificationMessage, ResponseMessage, RequestMessage, ErrorCodes
from kvls.utils import EOL_LSP, CHARSET

class MessageTest(unittest.TestCase):
    """ Server tests """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_notification_message(self):
        """ Test checking notification message build process
            and methods """
        params = '{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics",' \
                 '"params":{"uri":"path_to_document","diagnostics":[]}}'
        expected = 'Content-Length: {}{}Content-Type: ' \
                   'application/vscode-jsonrpc; charset={}{}{}{}'. \
                   format(len(params), EOL_LSP, "utf-8", EOL_LSP, EOL_LSP, params)
        message = NotificationMessage()
        message.content({'uri': "path_to_document",
                         'diagnostics': []}, 'textDocument/publishDiagnostics')
        result = message.build()
        self.assertEqual(expected, result)

    def test_response_message_success(self):
        """ Test checking success response message build process
            and methods """
        params = '{"jsonrpc":"2.0","id":12,"result":{}}'
        expected = 'Content-Length: {}{}Content-Type: ' \
                   'application/vscode-jsonrpc; charset={}{}{}{}'. \
                   format(len(params), EOL_LSP, "utf-8", EOL_LSP, EOL_LSP, params)
        message = ResponseMessage()
        message.content({}, True, 12)
        result = message.build()
        self.assertEqual(expected, result)

    def test_response_message_error(self):
        """Test checking error response message build process and methods."""
        params = '{"jsonrpc":"2.0","id":33,"error":{"code":-32700,"message":"ERROR"}}'
        expected = 'Content-Length: {}{}Content-Type: ' \
                   'application/vscode-jsonrpc; charset={}{}{}{}'. \
                   format(len(params), EOL_LSP, "utf-8", EOL_LSP, EOL_LSP, params)
        message = ResponseMessage()
        message.content({"code": ErrorCodes.PARSE_ERROR, "message": "ERROR"}, False, 33)
        result = message.build()
        self.assertEqual(expected, result)

    def test_request_message(self):
        """Test checking request message build process and methods."""
        params = '{"jsonrpc": "2.0", "id": 0, "method": "initialize", ' \
                 '"params": {"processId": 9484, "rootPath": "path_root"}}'
        content_length = 'Content-Length: {}'.format(len(params))
        content_type = 'Content-Type: application/vscode-jsonrpc; charset={}'.format("ascii")
        message = RequestMessage()
        message.content_length(content_length)
        message.content_type(content_type)
        message.content(params)
        self.assertEqual(message.jsonrpc(), "2.0")
        self.assertEqual(message.method(), "initialize")
        self.assertEqual(message.request_id(), 0)
        self.assertEqual(message.length, len(params))
        self.assertEqual(message.encoding, "ascii")
        self.assertEqual(message.params()["processId"], 9484)
        self.assertEqual(message.params()["rootPath"], "path_root")
        self.assertEqual(False, message.is_notification())

        content_type = '{}'.format(EOL_LSP)
        message_no_type = RequestMessage()
        message_no_type.content_length(content_length)
        message_no_type.content_type(content_type)
        message_no_type.content(params)
        self.assertEqual(message_no_type.jsonrpc(), "2.0")
        self.assertEqual(message_no_type.method(), "initialize")
        self.assertEqual(message_no_type.request_id(), 0)
        self.assertEqual(message_no_type.length, len(params))
        self.assertEqual(message_no_type.encoding, CHARSET)
        self.assertEqual(message_no_type.params()["processId"], 9484)
        self.assertEqual(message_no_type.params()["rootPath"], "path_root")
