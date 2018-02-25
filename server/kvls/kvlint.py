""" Simple KvLang linting module to show parser errors """
import os
# Disable stdout printout from kivy
os.environ["KIVY_NO_FILELOG"] = "1"
os.environ["KIVY_NO_CONSOLELOG"] = "1"
# Import Kivy parser
# Disable pylint warning, because environment variables must be set
# before import of module kivy
from kivy.lang.parser import Parser, ParserException # pylint: disable=C0413


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
        CODE: The diagnostic's code, which might appear in the user interface."""
    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4

    SOURCE = "kvlint"
    CODE = "KvLang100"

    def __init__(self):
        pass

    @classmethod
    def parser_exception(cls, file_content):
        """ Parse file content to catch ParserException from Kivy parser.
            This data from exception will be returned as list of the diagnostic
            elements stored in dictionary. Empty list is returned when there is
            no linting problems.

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
                'source' What source performed linting. Default to 'kvlint'.
                'message' Kvlint message. """
        diagnostic = []
        try:
            KvParser(content=file_content)
            # Diagnostic are clear. List will not be updated
        except ParserException as result:
            diagnostic.append({'range': {'start': {'line': result.line,
                                                   'character': 0},
                                         'end': {'line': result.line,
                                                 'character': 0}},
                               'severity': cls.ERROR,
                               'code': cls.CODE,
                               'source': cls.SOURCE,
                               'message': result.args[0].split('...')[2]})
        except SyntaxError as result:
            diagnostic.append({'range': {'start': {'line': result.lineno - 1,
                                                   'character': 0},
                                         'end': {'line': result.lineno - 1,
                                                 'character': 0}},
                               'severity': cls.ERROR,
                               'code': cls.CODE,
                               'source': cls.SOURCE,
                               'message': str(result.args[0])})
        return diagnostic
