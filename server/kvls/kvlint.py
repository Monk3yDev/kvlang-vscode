""" Simple KvLang linting module to show parser errors """
import os
# Disable stdout printout from kivy
os.environ["KIVY_NO_FILELOG"] = "1"
os.environ["KIVY_NO_CONSOLELOG"] = "1"
# Import Kivy parser
# Disable pylint warning, because environment variables must be set
# before import of module kivy
from kivy.lang.parser import Parser, ParserException # pylint: disable=C0413
from kvls.utils import EOL  # pylint: disable=C0413

class KvParser(Parser):
    """ Class only override method execute_directives.
        For more information see Class Parser """

    def execute_directives(self):
        """ Override method execute_directives.
            This method should do nothing. Current implementation
            of would always raise error during parsing includes in .kv files even
            when syntax is fine. Pure workaround."""
        pass

class KvLint(object):
    """ Class responsible for linting KvLang. Current implementation
        is simple using Parser from Kivy Project
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
            'message' KvLint message"""
    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4

    SOURCE = "KvLint"
    CODE = "KvLang100"

    def __init__(self, file_content):
        self.file_content = file_content

    def parse(self):
        """ Run all available parsers in the KvLint """
        diagnostic = []
        diagnostic.extend(self.parse_exception())
        diagnostic.extend(self.parse_information())
        return diagnostic

    def parse_exception(self):
        """ Parse file content to catch ParserException from Kivy parser.
            This data from exception will be returned as list of the diagnostic
            elements stored in dictionary. Empty list is returned when there is
            no linting problems."""
        diagnostic = []
        try:
            KvParser(content=self.file_content)
            # Diagnostic are clear. List will not be updated
        except ParserException as result:
            diagnostic.append({'range': {'start': {'line': result.line,
                                                   'character': 0},
                                         'end': {'line': result.line,
                                                 'character': 0}},
                               'severity': self.ERROR,
                               'code': self.CODE,
                               'source': self.SOURCE,
                               'message': result.args[0].split('...')[2]})
        except SyntaxError as result:
            diagnostic.append({'range': {'start': {'line': result.lineno - 1,
                                                   'character': 0},
                                         'end': {'line': result.lineno - 1,
                                                 'character': 0}},
                               'severity': self.ERROR,
                               'code': self.CODE,
                               'source': self.SOURCE,
                               'message': str(result.args[0])})
        return diagnostic

    def parse_information(self):
        """ Parse file content to catch problems other than exception.
            Empty list is returned when there is no linting problems.
            List of information:
                * Line to long
                * Trailing whitespace
                * Final newline missing
                * Trailing newlines
            """
        diagnostic = []
        line_index = 0
        for line in self.file_content.splitlines():
            length = len(line)
            if length >= 110:
                diagnostic.append({'range': {'start': {'line': line_index,
                                                       'character': 0},
                                             'end': {'line': line_index,
                                                     'character': 0}},
                                   'severity': self.INFORMATION,
                                   'code': self.CODE,
                                   'source': self.SOURCE,
                                   'message': "Line to long ({},{})".format(length, 110)})
            if length >= 1:
                if line[length-1].isspace():
                    diagnostic.append({'range': {'start': {'line': line_index,
                                                           'character': 0},
                                                 'end': {'line': line_index,
                                                         'character': 0}},
                                       'severity': self.INFORMATION,
                                       'code': self.CODE,
                                       'source': self.SOURCE,
                                       'message': "Trailing whitespace"})
            line_index += 1

        lines = self.file_content.splitlines(True)
        length = len(lines)
        if length >= 1 and lines[length-1].find(EOL) == -1:
            diagnostic.append({'range': {'start': {'line': length-1,
                                                   'character': 0},
                                         'end': {'line': length-1,
                                                 'character': 0}},
                               'severity': self.INFORMATION,
                               'code': self.CODE,
                               'source': self.SOURCE,
                               'message': "Final newline missing"})

        if length >= 1 and lines[length-1].find(EOL) != -1 and lines[length-1].isspace():
            diagnostic.append({'range': {'start': {'line': length-1,
                                                   'character': 0},
                                         'end': {'line': length-1,
                                                 'character': 0}},
                               'severity': self.INFORMATION,
                               'code': self.CODE,
                               'source': self.SOURCE,
                               'message': "Trailing newlines"})
        return diagnostic
