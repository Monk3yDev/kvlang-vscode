"""Unit tests for KvLint module."""
from __future__ import absolute_import
import unittest
import os
# Disable UnitTest.
os.environ["KIVY_UNITTEST"] = "0"
import kvls.kvlint as KV # pylint: disable=C0413
from kvls.utils import EOL # pylint: disable=C0413
from kvls.document import TextDocumentItem # pylint: disable=C0413


class KvLintTest(unittest.TestCase):
    """KvLint UnitTest."""

    def setUp(self):
        """Create parameters required to run unit tests."""
        self.kv_document = TextDocumentItem("file.kv", "kv", "")
        self.python_document = TextDocumentItem("file.py", "python", "")
        self.other_document = TextDocumentItem("file.txt", "txt", "")
        self.kvlint = KV.KvLint()

    def tearDown(self):
        """Cleanup of the tests."""
        pass

    def test_parse_exception(self):
        """Test check ParserException from Kivy parser."""
        self.kv_document.text = "<Widget>:"
        self.assertEqual(KV.parse_exception(self.kv_document, self.kv_document.beginning_index),
                         None)

	    # Negative diagnostic
        self.kv_document.text = "<AnchorLayout"
        diagnostic = KV.parse_exception(self.kv_document, self.kv_document.beginning_index)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Invalid rule (must be inside <>)")
        # Negative diagnostic EOL
        self.kv_document.text = "AnchorLayout: {}    height: '28sp".format(EOL)
        diagnostic = KV.parse_exception(self.kv_document, self.kv_document.beginning_index)
        self.assertEqual(diagnostic["range"]["start"]['line'], 1)
        self.assertEqual(diagnostic["range"]["end"]['line'], 1)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "EOL while scanning string literal")

    def test_parse_base_exception(self):
        """Test check BaseException from Kivy parser."""
        self.kv_document.text = 'Label<>:{}  size: 123{}    ' \
                                'width: 12 // 12{}    size: 1{}{}'''.format(EOL, EOL, EOL, EOL, EOL)
        diagnostic = KV.parse_exception(self.kv_document, self.kv_document.beginning_index)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"],
                         "Kivy parser exception: 'NoneType' object is not subscriptable")

    def test_parse(self):
        """Test check common register diagnostics."""
        self.kv_document.text = ""
        diagnostics = self.kvlint.parse(self.kv_document)
        self.assertIsInstance(diagnostics, list)
        self.assertEqual(len(diagnostics), 0)

        self.kv_document.text = "<A>:  " + EOL + EOL
        diagnostics = self.kvlint.parse(self.kv_document)
        self.assertIsInstance(diagnostics, list)
        self.assertEqual(len(diagnostics), 2)

    def test_common_validation(self):
        """Test check common validation."""
        diagnostic = KV.trailing_whitespace("NewLine    ", 99)
        self.assertEqual(diagnostic["range"]["start"]['line'], 99)
        self.assertEqual(diagnostic["range"]["end"]['line'], 99)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Trailing whitespace")

        diagnostic = KV.line_to_long("".join(["a" for x in range(0, 120)]), 0)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Line to long ({},{})".format(120, 110))

    def test_new_line_validation(self):
        """Test check newlines validation."""
        self.kv_document.text = "" + EOL
        diagnostic = KV.trailing_newline(self.kv_document, self.kv_document.beginning_index)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Trailing newlines")

        self.kv_document.text = "NewLine"
        diagnostic = KV.newline_missing(self.kv_document, self.kv_document.beginning_index)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Final newline missing")

    def test_parse_python(self):
        """Test check parsing embedded KvLang language in python file."""
        self.python_document.text = 'BOOL = true{}#<KvLang>{}<AnchorLayout{}#</KvLang>'\
                                    .format(EOL, EOL, EOL)
        diagnostics = self.kvlint.parse(self.python_document)
        self.assertIsInstance(diagnostics, list)
        self.assertEqual(len(diagnostics), 1)
        if len(diagnostics) == 1:
            self.assertEqual(diagnostics[0]["range"]["start"]['line'], 2)
            self.assertEqual(diagnostics[0]["range"]["end"]['line'], 2)
            self.assertEqual(diagnostics[0]["range"]["start"]['character'], 0)
            self.assertEqual(diagnostics[0]["range"]["end"]['character'], 0)
            self.assertEqual(diagnostics[0]["message"], "Invalid rule (must be inside <>)")

        # Lack of embedded kvlang in python file
        self.python_document.text = '#<KvLang>{}<AnchorLayout{}#</KvLa'.format(EOL, EOL)
        diagnostics = self.kvlint.parse(self.python_document)
        self.assertIsInstance(diagnostics, list)
        self.assertEqual(len(diagnostics), 0)

    def test_parse_other(self):
        """Test check parsing other file than python and kv."""
        self.other_document.text = '#<KvLang>{}<AnchorLayout{}#</KvLang>'.format(EOL, EOL)
        diagnostic = self.kvlint.parse(self.other_document)
        self.assertEqual(len(diagnostic), 0)
