"""Integration tests for KvLangServer."""
from __future__ import absolute_import
import unittest
import os
# Disable UnitTest.
os.environ["KIVY_UNITTEST"] = "0"
from kvls.kvlangserver import KvLangServer # pylint: disable=C0413


class ServerTest(unittest.TestCase):
    """Server tests."""

    def setUp(self):
        """Create parameters required to run unit tests."""
        self.stdin = open('./server/tests/initialized.txt', mode='r')
        self.diagnostic = open('./server/tests/diagnostic.txt', mode='r')
        self.unknown = open('./server/tests/unknown.txt', mode='r')
        self.stdout = open('./server/tests/stdout.txt', mode='w')

    def tearDown(self):
        """Cleanup of the tests."""
        self.stdin.close()
        self.stdout.close()
        self.diagnostic.close()

    def test_initialized(self):
        """Test check basic message flow from initialize to exit notification."""
        server = KvLangServer(self.stdin, self.stdout)
        server_exit_code = server.run()
        self.assertEqual(server_exit_code, KvLangServer.EXIT_SUCCESS)

    def test_diagnostic(self):
        """Test check basic diagnostic flow of the specific notification.

        DidCloseTextDocumentParams
        DidSaveTextDocument
        DidOpenTextDocumentParams.

        """
        server = KvLangServer(self.diagnostic, self.stdout)
        server_exit_code = server.run()
        # Check if server closed properly.
        self.assertEqual(server_exit_code, KvLangServer.EXIT_SUCCESS)
        results = open('./server/tests/stdout.txt', mode='r')
        content = "".join(results.readlines())
        results.close()
        # Diagnostic DidCloseTextDocumentParams
        find = '{"jsonrpc":"2.0","method":"textDocument/' \
               'publishDiagnostics","params":{"uri":"kivy.kv"' \
               ',"diagnostics":[]}}'
        self.assertNotEqual(content.find(find), -1)
        # Diagnostic DidSaveTextDocument
        find = '{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{"uri":' \
               '"kivy.kv","diagnostics":['
        self.assertNotEqual(content.find(find), -1)
        find = '{"range":{"start":{"line":0,"character":0},"end":' \
               '{"line":0,"character":0}},"severity":1,"code":"E001","source":"KvLint"' \
               ',"message":"Invalid data after declaration"}'
        self.assertNotEqual(content.find(find), -1)
        # Diagnostic DidOpenTextDocumentParams
        find = '{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{"uri":' \
               '"kivy.kv","diagnostics":['
        self.assertNotEqual(content.find(find), -1)
        find = '{"range":{"start":{"line":0,"character":0},"end":' \
               '{"line":0,"character":0}},"severity":1,"code":"E001","source":"KvLint"' \
               ',"message":"Invalid rule (must be inside <>)"}'
        self.assertNotEqual(content.find(find), -1)

    def test_unknown_method(self):
        """Test check basic message flow from initialize to unknown method."""
        server = KvLangServer(self.unknown, self.stdout)
        server_exit_code = server.run()
        self.assertEqual(server_exit_code, KvLangServer.EXIT_SUCCESS)
        results = open('./server/tests/stdout.txt', mode='r')
        content = "".join(results.readlines())
        results.close()
        find = '{"jsonrpc":"2.0","id":12,"error":{"code":-32601,"message":"Method not found"}}'
        self.assertNotEqual(content.find(find), -1)
        first = content.find("Method not found")
        second = content.find("Method not found", len("Method not found") + first)
        self.assertNotEqual(first, -1)
        self.assertEqual(second, -1)


    def test_initialized_with_message(self):
        """Test check message notification to client during initialized method."""
        server = KvLangServer(self.stdin, self.stdout)
        server.kvlint.KIVY_IMPORTED = False
        server_exit_code = server.run()
        self.assertEqual(server_exit_code, KvLangServer.EXIT_SUCCESS)
        results = open('./server/tests/stdout.txt', mode='r')
        content = "".join(results.readlines())
        results.close()
        self.assertNotEqual(content.find("KvLint was not able import kivy module."), -1)
