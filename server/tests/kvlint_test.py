""" Unit tests for KvLint module """
import unittest
from kvls.kvlint import KvLint
from kvls.utils import EOL

class KvLintTest(unittest.TestCase):
    """ Server tests """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_kvlint_parser(self):
        """ Basic lint test """
        kvlint = KvLint()
        positive_parsing = kvlint.parser_exception("<Widget>:")
        negative_parsing = kvlint.parser_exception("<AnchorLayout")
        negative_parsing_eol = kvlint.parser_exception("AnchorLayout: {}    height: '28sp" \
                                     .format(EOL))
        self.assertEqual(positive_parsing, None)
        self.assertEqual(negative_parsing.severity, 1)
        self.assertEqual(negative_parsing.start['line'], 0)
        self.assertEqual(negative_parsing.end['line'], 0)
        self.assertEqual(negative_parsing.message, "\nInvalid rule (must be inside <>)")
        # Negative parsing EOL
        self.assertEqual(negative_parsing_eol.severity, 1)
        self.assertEqual(negative_parsing_eol.start['line'], 1)
        self.assertEqual(negative_parsing_eol.end['line'], 1)
        self.assertEqual(negative_parsing_eol.message, "EOL while scanning string literal")
