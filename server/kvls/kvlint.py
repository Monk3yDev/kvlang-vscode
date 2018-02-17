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


class KvLintResult(object):
    """ KvLint result object
        start: Contains line and position of first character.
        end: Contains line and position of last character.
        severity: Severity of the lint result.
        code: Diagnostic code.
        source: What source performed linting. Default to 'kvlint'.
        message: Kvlint message.
    """
    def __init__(self):
        self.start = {'line': 0, 'character': 0}
        self.end = {'line': 0, 'character': 0}
        self.severity = 1
        self.code = "KvLang100"
        self.source = "kvlint"
        self.message = ""

class KvLint(object):
    """ Class responsible for linting KvLang. Current implementation
        is simple using Parser from Kivy Project """
    def __init__(self):
        pass

    @staticmethod
    def parser_exception(file_content):
        """ Parse file content to catch ParserException
            from Kivy parser. This data from exception
            will be returned in KvLintResult object. If
            parsing is success return will be None"""
        parser_result = None
        try:
            KvParser(content=file_content)
            parser_result = None
        except ParserException as result:
            parser_result = KvLintResult()
            parser_result.start['line'] = result.line
            parser_result.end['line'] = result.line
            parser_result.message = result.args[0].split('...')[2]
            parser_result.severity = 1
        except SyntaxError as result:
            parser_result = KvLintResult()
            parser_result.start['line'] = result.lineno - 1
            parser_result.end['line'] = result.lineno - 1
            parser_result.message = str(result.args[0])
            parser_result.severity = 1
        return parser_result
