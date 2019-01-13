"""Script which start KvLang Language Server."""
from __future__ import absolute_import
import sys
from kvls.kvlangserver import KvLangServer

if __name__ == "__main__":
    SERVER = KvLangServer(sys.stdin, sys.stdout)
    SERVER_EXIT_CODE = SERVER.run()
    sys.exit(SERVER_EXIT_CODE)
