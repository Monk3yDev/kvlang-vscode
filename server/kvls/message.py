"""Module responsible for parsing and storing information from the stdin and stdout.

Client use stdin and the server stdout I/O.

"""
from __future__ import absolute_import
import re
import json
from kvls.utils import EOL_LSP, CHARSET

class MessageUtils(object):
    """Helper class for processing message information."""

    @staticmethod
    def fetch_content_length(line):
        """Fetch content length from the header."""
        match = re.match('Content-Length: ([0-9]*)', line)
        return int(match.group(1))

    @staticmethod
    def fetch_charset(line):
        """Fetch charset from the content type header."""
        match = re.match('Content-Type: .*charset=(.*)', line)
        if match is not None:
            return match.group(1)
        return None

    @staticmethod
    def parse_content(content, charset):
        """Parse JSON content to the dictionary using specific charset."""
        return json.loads(content, encoding=charset)

    @staticmethod
    def is_notification(content):
        """Check is message from client is notification."""
        return content.get("id", None) is None

class Message(object):
    """Base class of the language server protocol specification."""

    def __init__(self):
        """Initialize base message object."""
        self.message_content = dict()

    @property
    def jsonrpc(self):
        """Return jsonrpc version."""
        return self.message_content["jsonrpc"]

    def build(self):
        """Build and return full content of the message."""
        message_content = json.dumps(self.message_content, separators=(',', ':'))
        length = len(message_content)
        return 'Content-Length: {}{}Content-Type: ' \
               'application/vscode-jsonrpc; charset={}{}{}{}'. \
               format(length, EOL_LSP, CHARSET, EOL_LSP, EOL_LSP, message_content)

class NotificationMessage(Message):
    """Class responsible storing notification message information."""

    def content(self, content, method):
        """Assign content and method to the message."""
        self.message_content = {"jsonrpc": "2.0", "method": method, "params": content}

    def assign_message_content(self, dict_content):
        """Full dictionary content of the message which will be assigned to notification."""
        self.message_content = dict_content

    @property
    def method(self):
        """Return method name."""
        return self.message_content["method"]

    @property
    def params(self):
        """Return params included in notification."""
        return self.message_content["params"]

class ResponseMessage(Message):
    """Class responsible storing response message information."""

    def content(self, content, success, request_id):
        """Assign content, request ID, result or error message depends on the success."""
        if success:
            self.message_content = {"jsonrpc": "2.0", "id": request_id, "result": content}
        else:
            self.message_content = {"jsonrpc": "2.0", "id": request_id, "error": content}

    @property
    def request_id(self):
        """Return id of the request."""
        return self.message_content["id"]

    @property
    def result(self):
        """Return result included in response."""
        return self.message_content["result"]

    @property
    def error(self):
        """Return error included in response."""
        return self.message_content["error"]

class RequestMessage(Message):
    """Class responsible storing request message information."""

    def assign_message_content(self, dict_content):
        """Full dictionary content of the message which will be assigned to request."""
        self.message_content = dict_content

    @property
    def request_id(self):
        """Return id of the request."""
        return self.message_content["id"]

    @property
    def method(self):
        """Return method name."""
        return self.message_content["method"]

    @property
    def params(self):
        """Return params included in request."""
        return self.message_content["params"]

class ErrorCodes(object):
    """The error constants in case a request fails."""

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


class MessageType(object):
    """Message types used for displaying message in client/server."""

    ERROR = 1
    WARNING = 2
    INFO = 3
    LOG = 3
