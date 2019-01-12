""" Integration tests for KvLangServer """
from __future__ import absolute_import
import unittest
import os
# Disable UnitTest.
os.environ["KIVY_UNITTEST"] = "0"
from kvls.kvlangserver import KvLangServer # pylint: disable=C0413


class ServerTest(unittest.TestCase):
    """ Server tests """
    def setUp(self):
        self.stdin = open('./server/tests/initialized.txt', mode='r')
        self.diagnostic = open('./server/tests/diagnostic.txt', mode='r')
        self.stdout = open('./server/tests/stdout.txt', mode='w')

    def tearDown(self):
        self.stdin.close()
        self.stdout.close()
        self.diagnostic.close()

    def test_server_initialized(self):
        """ Test check basic message flow from initialize
            to exist notification """
        server = KvLangServer(self.stdin, self.stdout)
        server_exit_code = server.run()
        self.assertEqual(server_exit_code, KvLangServer.EXIT_SUCCESS)

    def test_server_diagnostic(self):
        """ Test check basic diagnostic flow
            during notification DidCloseTextDocumentParams/
            DidSaveTextDocument/DidOpenTextDocumentParams """
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
               '{"line":0,"character":0}},"severity":1,"code":"KvLang100","source":"KvLint"' \
               ',"message":"\\nInvalid data after declaration"}'
        self.assertNotEqual(content.find(find), -1)
        # Diagnostic DidOpenTextDocumentParams
        find = '{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{"uri":' \
               '"kivy.kv","diagnostics":['
        self.assertNotEqual(content.find(find), -1)
        find = '{"range":{"start":{"line":0,"character":0},"end":' \
               '{"line":0,"character":0}},"severity":1,"code":"KvLang100","source":"KvLint"' \
               ',"message":"\\nInvalid rule (must be inside <>)"}'
        self.assertNotEqual(content.find(find), -1)
