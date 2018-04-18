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

    def test_kvlint_parse_exception(self):
        """ Test check ParserException from Kivy parser"""
        kvlint = KvLint("<Widget>:")
        positive_diagnostic = kvlint.parse_exception()
        kvlint = KvLint("<AnchorLayout")
        negative_diagnostic = kvlint.parse_exception()
        kvlint = KvLint("AnchorLayout: {}    height: '28sp".format(EOL))
        negative_diagnostic_eol = kvlint.parse_exception()
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

    def test_kvlint_parse_information(self):
        """ Test check report information from parser """
        kvlint = KvLint("".join(["a" for x in range(0, 120)])+EOL)
        line_to_long = kvlint.parse_information()
        self.assertIsInstance(line_to_long, list)

	    # Line to long diagnostic
        self.assertEqual(len(line_to_long), 1)
        diagnostic = line_to_long.pop()
        self.assertEqual(diagnostic["severity"], KvLint.INFORMATION)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Line to long ({},{})".format(120, 110))
        self.assertEqual(diagnostic["source"], KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KvLint.CODE)

	    # Trailing newlines
        kvlint = KvLint(""+EOL)
        trailing_newlines = kvlint.parse_information()
        self.assertIsInstance(trailing_newlines, list)

        self.assertEqual(len(trailing_newlines), 1)
        diagnostic = trailing_newlines.pop()
        self.assertEqual(diagnostic["severity"], KvLint.INFORMATION)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Trailing newlines")
        self.assertEqual(diagnostic["source"], KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KvLint.CODE)

	    # Newline missing
        kvlint = KvLint("NewLine")
        new_line = kvlint.parse_information()
        self.assertIsInstance(new_line, list)

        self.assertEqual(len(new_line), 1)
        diagnostic = new_line.pop()
        self.assertEqual(diagnostic["severity"], KvLint.INFORMATION)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Final newline missing")
        self.assertEqual(diagnostic["source"], KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KvLint.CODE)

	    # Trailing whitespace
        kvlint = KvLint("NewLine    "+EOL)
        trailing_whitespace = kvlint.parse_information()
        self.assertIsInstance(trailing_whitespace, list)

        self.assertEqual(len(trailing_whitespace), 1)
        diagnostic = trailing_whitespace.pop()
        self.assertEqual(diagnostic["severity"], KvLint.INFORMATION)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Trailing whitespace")
        self.assertEqual(diagnostic["source"], KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KvLint.CODE)

	    # Empty file
        kvlint = KvLint("")
        empty_file = kvlint.parse()
        self.assertIsInstance(empty_file, list)
        self.assertEqual(len(empty_file), 0)
