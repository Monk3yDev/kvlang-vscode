"""Simple KvLang linting module to show parser errors."""
from __future__ import absolute_import
import os
import re
# Disable stdout printout from kivy
os.environ["KIVY_NO_FILELOG"] = "1"
os.environ["KIVY_NO_CONSOLELOG"] = "1"
# Import Kivy parser
# Disable pylint warning, because environment variables must be set
# before import of module kivy
from kivy.lang import Parser, ParserException # pylint: disable=C0413
from kvls.utils import EOL  # pylint: disable=C0413

SINGLE_RULE = re.compile("^<[a-zA-Z0-9_\\- ]+>:")

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
        ERROR: Reports an error.
        WARNING: Reports a warning.
        INFORMATION: Reports an information.
        HINT: Reports a hint.
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

    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4

    SOURCE = "KvLint"
    CODE = "KvLang100"

    def __init__(self):
        """Initialize KvLint object."""
        pass

    def parse(self, document):
        """Run all available parsers in the KvLint."""
        diagnostic = []
        diagnostic.extend(self.parse_exception(document))
        diagnostic.extend(self.parse_other(document))
        return diagnostic

    def parse_exception(self, document):
        """Parse file content to catch ParserException from Kivy parser."""
        diagnostic = []
        try:
            KvParser(content=document.text)
            # Diagnostic are clear. List will not be updated
        except ParserException as exception:
            diagnostic.append({'range': {'start': {'line': exception.line,
                                                   'character': 0},
                                         'end': {'line': exception.line,
                                                 'character': 0}},
                               'severity': self.ERROR,
                               'code': self.CODE,
                               'source': self.SOURCE,
                               'message': exception.args[0].split('...')[2]})
        except SyntaxError as exception:
            diagnostic.append({'range': {'start': {'line': exception.lineno - 1,
                                                   'character': 0},
                                         'end': {'line': exception.lineno - 1,
                                                 'character': 0}},
                               'severity': self.ERROR,
                               'code': self.CODE,
                               'source': self.SOURCE,
                               'message': str(exception.args[0])})
        except BaseException as exception:
            diagnostic.append({'range': {'start': {'line': 0,
                                                   'character': 0},
                                         'end': {'line': 0,
                                                 'character': 0}},
                               'severity': self.ERROR,
                               'code': self.CODE,
                               'source': self.SOURCE,
                               'message': "Kivy parser exception: " + str(exception)})

        return diagnostic

    def parse_other(self, document):
        """Parse file content to catch problems other than exception."""
        diagnostic = []
        line_index = 0
        for line in document.text.splitlines():
            diagnostic.extend(common_validation(line, line_index))
            diagnostic.extend(rule_validation(line, line_index))
            line_index += 1
        lines = document.text.splitlines(True)
        length = len(lines)
        if length >= 1:
            diagnostic.extend(new_line_validation(lines[length-1], length-1))
        return diagnostic


def new_line_validation(line, line_index):
    """Perform lint check with newlines."""
    diagnostic = []
    if line.find(EOL) == -1:
        diagnostic.append({'range': {'start': {'line': line_index,
                                               'character': 0},
                                     'end': {'line': line_index,
                                             'character': 0}},
                           'severity': KvLint.INFORMATION,
                           'code': KvLint.CODE,
                           'source': KvLint.SOURCE,
                           'message': "Final newline missing"})

    if line.find(EOL) != -1 and line.isspace():
        diagnostic.append({'range': {'start': {'line': line_index,
                                               'character': 0},
                                     'end': {'line': line_index,
                                             'character': 0}},
                           'severity': KvLint.INFORMATION,
                           'code': KvLint.CODE,
                           'source': KvLint.SOURCE,
                           'message': "Trailing newlines"})
    return diagnostic


def common_validation(line, line_index):
    """Perform lint check on the line."""
    diagnostic = []
    length = len(line)
    if length >= 110:
        diagnostic.append({'range': {'start': {'line': line_index,
                                               'character': 0},
                                     'end': {'line': line_index,
                                             'character': 0}},
                           'severity': KvLint.INFORMATION,
                           'code': KvLint.CODE,
                           'source': KvLint.SOURCE,
                           'message': "Line to long ({},{})".format(length, 110)})
    if length >= 1:
        if line[length-1].isspace():
            diagnostic.append({'range': {'start': {'line': line_index,
                                                   'character': 0},
                                         'end': {'line': line_index,
                                                 'character': 0}},
                               'severity': KvLint.INFORMATION,
                               'code': KvLint.CODE,
                               'source': KvLint.SOURCE,
                               'message': "Trailing whitespace"})
    return diagnostic


def rule_validation(line, line_index):
    """Run all KvLang rule validations."""
    diagnostic = []
    if SINGLE_RULE.match(line):
        diagnostic.extend(single_rule_validation(line, line_index))
    return diagnostic


def single_rule_validation(line, line_index):
    """Perform lint check on single widget rule."""
    diagnostic = []
    if single_rule_dash(line):
        diagnostic.append({'range': {'start': {'line': line_index,
                                               'character': 0},
                                     'end': {'line': line_index,
                                             'character': 0}},
                           'severity': KvLint.WARNING,
                           'code': KvLint.CODE,
                           'source': KvLint.SOURCE,
                           'message': "Improper handling of '-' in KvLang rule"})
    if rule_whitespace(line):
        diagnostic.append({'range': {'start': {'line': line_index,
                                               'character': 0},
                                     'end': {'line': line_index,
                                             'character': 0}},
                           'severity': KvLint.INFORMATION,
                           'code': KvLint.CODE,
                           'source': KvLint.SOURCE,
                           'message': "Whitespace in KvLang rule"})
    return diagnostic


def single_rule_dash(line):
    """Check if single rule is build properly with dash."""
    if line.find("-") in (-1, 1) and line.count('-') <= 1:
        return False
    return True


def rule_whitespace(line):
    """Check if rule is build without whitespace."""
    for character in line:
        if character != '>':
            if character.isspace():
                return True
        else:
            break
    return False
