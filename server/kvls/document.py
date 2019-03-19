"""Module contains classes responsible for document’s management in the language server."""

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
        self.text = text
