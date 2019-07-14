"""Simple KvLang linting module to show parser errors."""
from __future__ import absolute_import
from kvls.utils import EOL  # pylint: disable=C0413
from kvls.lang import Parser, ParserException, KIVY_IMPORTED, KIVY_IMPORT_MSG

class Severity(object):
    """Data class of the lint result.

    Severity explanation:
        ERROR: Reports an error.
        WARNING: Reports a warning.
        INFORMATION: Reports an information.
        HINT: Reports a hint.

    """

    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4

class KvParser(Parser):
    """Class only override method execute_directives."""

    def execute_directives(self):
        """Override method execute_directives.

        This method should do nothing. Current implementation of would always raise error during
        parsing includes in .kv files even when syntax is fine. Pure workaround.

        """
        pass

class KvLint(object):
    """Class responsible for linting KvLang.

    Current implementation is simple using Parser from Kivy Project
        SOURCE: A human-readable string describing the source of diagnostic.
        CODE: The diagnostic's code, which might appear in the user interface.

    KvLint diagnostic result dictionary contains
        'range' Contains line and position of start and end character.
            'start'
                'line'
                'character'
            'end'
                'line'
                'character'
        'severity' Severity of the lint result.
        'code' Diagnostic code.
        'source' What source performed linting. Default to 'KvLint'.
        'message' KvLint message

    """

    SOURCE = "KvLint"
    KIVY_IMPORTED = KIVY_IMPORTED
    KIVY_IMPORT_MSG = KIVY_IMPORT_MSG

    def __init__(self):
        """Initialize KvLint object."""
        self.single_line = dict()
        self.full_document = dict()
        self.register_line(line_to_long, Severity.INFORMATION, "I001", KvLint.SOURCE)
        self.register_line(trailing_whitespace, Severity.INFORMATION, "I002", KvLint.SOURCE)

        self.register_document(newline_missing, Severity.INFORMATION, "I003", KvLint.SOURCE)
        self.register_document(trailing_newline, Severity.INFORMATION, "I004", KvLint.SOURCE)
        self.register_document(parse_exception, Severity.ERROR, "E001", KvLint.SOURCE)

    def register_line(self, method, severity, code, source):
        """Register single line diagnostic."""
        self.single_line[code] = (method, severity, source)

    def register_document(self, method, severity, code, source):
        """Register full document diagnostic."""
        self.full_document[code] = (method, severity, source)

    def parse(self, document):
        """Run all available diagnostic in the KvLint."""
        diagnostics = []
        line_index = 0
        beginning_index = document.beginning_index
        for line in document.text.splitlines():
            for code, values in self.single_line.items():
                method, severity, source = values
                diagnostic = method(line, beginning_index + line_index)
                if diagnostic:
                    diagnostics.append({'range': diagnostic["range"],
                                        'severity': severity, 'code': code,
                                        'source': source, 'message': diagnostic["message"]})
            line_index += 1
        for code, values in self.full_document.items():
            method, severity, source = values
            diagnostic = method(document, beginning_index)
            if diagnostic:
                diagnostics.append({'range': diagnostic["range"],
                                    'severity': severity, 'code': code,
                                    'source': source, 'message': diagnostic["message"]})
        return diagnostics

def line_to_long(line, line_index):
    """Check if line is not to long."""
    length = len(line)
    if length >= 110:
        return {'range': {'start': {'line': line_index,
                                    'character': 0},
                          'end': {'line': line_index,
                                  'character': 0}},
                'message': "Line to long ({},{})".format(length, 110)}
    return None

def trailing_whitespace(line, line_index):
    """Check if line contain trailing whitespace."""
    length = len(line)
    if length >= 1:
        if line[length-1].isspace():
            return {'range': {'start': {'line': line_index,
                                        'character': 0},
                              'end': {'line': line_index,
                                      'character': 0}},
                    'message': "Trailing whitespace"}
    return None

def newline_missing(document, beginning_index):
    """Check if document contain newline."""
    lines = document.text.splitlines(True)
    length = len(lines)
    if length >= 1:
        if lines[length-1].find(EOL) == -1:
            return {'range': {'start': {'line': beginning_index + length-1,
                                        'character': 0},
                              'end': {'line': beginning_index + length-1,
                                      'character': 0}},
                    'message': "Final newline missing"}
    return None

def trailing_newline(document, beginning_index):
    """Check if document contain trailing newline."""
    lines = document.text.splitlines(True)
    length = len(lines)
    if length >= 1:
        if lines[length-1].find(EOL) != -1 and lines[length-1].isspace():
            return {'range': {'start': {'line': beginning_index + length-1,
                                        'character': 0},
                              'end': {'line': beginning_index + length-1,
                                      'character': 0}},
                    'message': "Trailing newlines"}
    return None

def parse_exception(document, beginning_index):
    """Parse document to catch ParserException from Kivy parser."""
    try:
        KvParser(content=document.text)
        # Diagnostic are clear. List will not be updated
    except ParserException as exception:
        return {'range': {'start': {'line': beginning_index + exception.line,
                                    'character': 0},
                          'end': {'line': beginning_index + exception.line,
                                  'character': 0}},
                'message': exception.args[0].split('...')[2].strip()}
    except SyntaxError as exception:
        return {'range': {'start': {'line': beginning_index + exception.lineno - 1,
                                    'character': 0},
                          'end': {'line': beginning_index + exception.lineno - 1,
                                  'character': 0}},
                'message': str(exception.args[0])}
    except BaseException as exception:
        return {'range': {'start': {'line': beginning_index + 0,
                                    'character': 0},
                          'end': {'line': beginning_index + 0,
                                  'character': 0}},
                'message': "Kivy parser exception: " + str(exception)}

    return None
