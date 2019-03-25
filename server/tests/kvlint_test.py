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
        self.kv_document = TextDocumentItem("file.kv", "kv", "")
        self.kvlint = KV.KvLint()

    def tearDown(self):
        pass

    def test_parse_exception(self):
        """Test check ParserException from Kivy parser."""
        self.kv_document.text = "<Widget>:"
        positive_diagnostic = self.kvlint.parse_exception(self.kv_document)
        self.kv_document.text = "<AnchorLayout"
        negative_diagnostic = self.kvlint.parse_exception(self.kv_document)
        self.kv_document.text = "AnchorLayout: {}    height: '28sp".format(EOL)
        negative_diagnostic_eol = self.kvlint.parse_exception(self.kv_document)
        self.assertIsInstance(positive_diagnostic, list)
        self.assertListEqual(positive_diagnostic, [])

	    # Negative diagnostic
        self.assertEqual(len(negative_diagnostic), 1)
        diagnostic = negative_diagnostic.pop()
        self.assertEqual(diagnostic["severity"], KV.KvLint.ERROR)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "\nInvalid rule (must be inside <>)")
        self.assertEqual(diagnostic["source"], KV.KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KV.KvLint.CODE)

        # Negative diagnostic EOL
        self.assertEqual(len(negative_diagnostic_eol), 1)
        diagnostic = negative_diagnostic_eol.pop()
        self.assertEqual(diagnostic["severity"], KV.KvLint.ERROR)
        self.assertEqual(diagnostic["range"]["start"]['line'], 1)
        self.assertEqual(diagnostic["range"]["end"]['line'], 1)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "EOL while scanning string literal")
        self.assertEqual(diagnostic["source"], KV.KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KV.KvLint.CODE)

    def test_parse_base_exception(self):
        """Test check BaseException from Kivy parser."""
        self.kv_document.text = 'Label<>:\r\n  size: 123\r\n    ' \
                                'width: 12 // 12\r\n    size: 1\r\n\r\n'''
        parser_exception = self.kvlint.parse_exception(self.kv_document)
        self.assertIsInstance(parser_exception, list)

        self.assertEqual(len(parser_exception), 1)
        diagnostic = parser_exception.pop()
        self.assertEqual(diagnostic["severity"], KV.KvLint.ERROR)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"],
                         "Kivy parser exception: 'NoneType' object is not subscriptable")
        self.assertEqual(diagnostic["source"], KV.KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KV.KvLint.CODE)

    def test_parse_other(self):
        """Test check other validations."""
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
        diagnostics = KV.common_validation("NewLine    ", 99)
        self.assertEqual(len(diagnostics), 1)
        diagnostic = diagnostics.pop()
        self.assertEqual(diagnostic["severity"], KV.KvLint.INFORMATION)
        self.assertEqual(diagnostic["range"]["start"]['line'], 99)
        self.assertEqual(diagnostic["range"]["end"]['line'], 99)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Trailing whitespace")
        self.assertEqual(diagnostic["source"], KV.KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KV.KvLint.CODE)

        diagnostics = KV.common_validation("".join(["a" for x in range(0, 120)]), 0)
        self.assertEqual(len(diagnostics), 1)
        diagnostic = diagnostics.pop()
        self.assertEqual(diagnostic["severity"], KV.KvLint.INFORMATION)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Line to long ({},{})".format(120, 110))
        self.assertEqual(diagnostic["source"], KV.KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KV.KvLint.CODE)

    def test_new_line_validation(self):
        """Test check newlines validation."""
        diagnostics = KV.new_line_validation("" + EOL, 88)
        self.assertEqual(len(diagnostics), 1)
        diagnostic = diagnostics.pop()
        self.assertEqual(diagnostic["severity"], KV.KvLint.INFORMATION)
        self.assertEqual(diagnostic["range"]["start"]['line'], 88)
        self.assertEqual(diagnostic["range"]["end"]['line'], 88)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Trailing newlines")
        self.assertEqual(diagnostic["source"], KV.KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KV.KvLint.CODE)

        diagnostics = KV.new_line_validation("NewLine", 0)
        self.assertEqual(len(diagnostics), 1)
        diagnostic = diagnostics.pop()
        self.assertEqual(diagnostic["severity"], KV.KvLint.INFORMATION)
        self.assertEqual(diagnostic["range"]["start"]['line'], 0)
        self.assertEqual(diagnostic["range"]["end"]['line'], 0)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Final newline missing")
        self.assertEqual(diagnostic["source"], KV.KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KV.KvLint.CODE)

    def test_single_rule_dash(self):
        """Test check dash character in the single rule."""
        self.assertFalse(KV.single_rule_dash("<-Label>:"))
        self.assertTrue(KV.single_rule_dash("<-Label->:"))
        self.assertTrue(KV.single_rule_dash("<Label->:"))
        self.assertFalse(KV.single_rule_dash("<Label>:"))

    def test_rule_whitespace(self):
        """Test check whitespace character in the rule."""
        self.assertFalse(KV.rule_whitespace("<Label>:"))
        self.assertTrue(KV.rule_whitespace("<Label >:"))
        self.assertFalse(KV.rule_whitespace("<Label>:  "))

    def test_rule_validation(self):
        """Test check Kivy rule validations."""
        self.assertEqual(len(KV.rule_validation("<--Label >:", 10)), 2)
        self.assertEqual(len(KV.rule_validation("<-La@bel>:", 10)), 0)

    def test_single_rule_validation(self):
        """Test check rule validation."""
        diagnostics = KV.single_rule_validation("<--Label>:", 10)
        self.assertEqual(len(diagnostics), 1)
        diagnostic = diagnostics.pop()
        self.assertEqual(diagnostic["severity"], KV.KvLint.WARNING)
        self.assertEqual(diagnostic["range"]["start"]['line'], 10)
        self.assertEqual(diagnostic["range"]["end"]['line'], 10)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Improper handling of '-' in KvLang rule")
        self.assertEqual(diagnostic["source"], KV.KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KV.KvLint.CODE)

        diagnostics = KV.single_rule_validation("< Label>:", 10)
        self.assertEqual(len(diagnostics), 1)
        diagnostic = diagnostics.pop()
        self.assertEqual(diagnostic["severity"], KV.KvLint.INFORMATION)
        self.assertEqual(diagnostic["range"]["start"]['line'], 10)
        self.assertEqual(diagnostic["range"]["end"]['line'], 10)
        self.assertEqual(diagnostic["range"]["start"]['character'], 0)
        self.assertEqual(diagnostic["range"]["end"]['character'], 0)
        self.assertEqual(diagnostic["message"], "Whitespace in KvLang rule")
        self.assertEqual(diagnostic["source"], KV.KvLint.SOURCE)
        self.assertEqual(diagnostic["code"], KV.KvLint.CODE)
