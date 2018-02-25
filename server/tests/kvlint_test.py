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
        positive_diagnostic = kvlint.parser_exception("<Widget>:")
        negative_diagnostic = kvlint.parser_exception("<AnchorLayout")
        negative_diagnostic_eol = kvlint.parser_exception("AnchorLayout: {}    height: '28sp" \
                                                          .format(EOL))
        self.assertIsInstance(positive_diagnostic, list)
        self.assertListEqual(positive_diagnostic, [])

        # Negative diagnostic
        self.assertEqual(len(negative_diagnostic), 1)
        diagnostic = negative_diagnostic.pop()
        self.assertEqual(diagnostic["severity"], KvLint.ERROR)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "\nInvalid rule (must be inside <>)")
        self.assertEqual(diagnostic["source"], KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KvLint.CODE)

        # Negative diagnostic EOL
        self.assertEqual(len(negative_diagnostic_eol), 1)
        diagnostic = negative_diagnostic_eol.pop()
        self.assertEqual(diagnostic["severity"], KvLint.ERROR)
        self.assertEqual(diagnostic["range"]["start"]['line'], 1)
        self.assertEqual(diagnostic["range"]["end"]['line'], 1)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "EOL while scanning string literal")
        self.assertEqual(diagnostic["source"], KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KvLint.CODE)
