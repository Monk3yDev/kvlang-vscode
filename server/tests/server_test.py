""" Integration tests for KvLangServer """
import unittest
from kvls.kvlangserver import KvLangServer

class ServerTest(unittest.TestCase):
    """ Server tests """
    def setUp(self):
        self.stdin = open('./server/tests/initialized.txt', mode='r')
        self.stdout = open('./server/tests/stdout.txt', mode='w')

    def tearDown(self):
        self.stdin.close()
        self.stdout.close()

    def test_server_initialized(self):
        """ Test check basic message flow from initialize
            to exist notification """
        server = KvLangServer(self.stdin, self.stdout)
        server_exit_code = server.run()
        self.assertEqual(server_exit_code, KvLangServer.EXIT_SUCCESS)
