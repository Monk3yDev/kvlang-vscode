"""Module contains classes responsible for document's management in the language server."""
from __future__ import absolute_import
import re
from kvls.utils import EOL

KVLANG_TAG = re.compile("(#<KvLang>[\\S\\s]*?#<\\/KvLang>)")
KVLANG_TAG_BEGIN = re.compile("#<KvLang>")

class TextDocumentManager(object):
    """Manager of the existing TextDocumentItem objects under language server."""

    def __init__(self):
        """Initialize document manager."""
        self.documents = dict()

    def add(self, document):
        """Add new document to the manager."""
        self.documents[document.uri] = document

    def remove(self, uri):
        """Remove document from the manager."""
        self.documents.pop(uri)

    def get(self, uri):
        """Return specific document from the manager."""
        return self.documents[uri]

class TextDocumentItem(object):
    """Class store information related to specific document item."""

    def __init__(self, uri, language_id, text):
        """Initialize text document item."""
        self.uri = uri
        self.language_id = language_id
        self.__text = text

    @property
    def text(self):
        """Return document text for specific language id."""
        if self.language_id == LanguageId.PYTHON:
            match = KVLANG_TAG.search(self.__text)
            if match:
                return match.group() + EOL
        elif self.language_id == LanguageId.KVLANG:
            return self.__text
        return ""

    @text.setter
    def text(self, value):
        """Set new content of the document."""
        self.__text = value

    @property
    def beginning_index(self):
        """Return line index where KvLang start in document."""
        if self.language_id == LanguageId.PYTHON:
            lines = self.__text.splitlines()
            line_index = 0
            for line in lines:
                match = KVLANG_TAG_BEGIN.search(line)
                if match:
                    return line_index
                line_index += 1
        return 0

class LanguageId(object):
    """Language identifier to identify a document on the server side."""

    PYTHON = "python"
    KVLANG = "kv"
