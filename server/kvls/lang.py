"""Module import kivy Parser is available. Otherwise fake class is created."""
from __future__ import absolute_import
import os
# Disable stdout printout from kivy
os.environ["KIVY_NO_FILELOG"] = "1"
os.environ["KIVY_NO_CONSOLELOG"] = "1"
# Import Kivy parser
# Disable pylint warning, because environment variables must be set
# before import of module kivy. Create fake classes when import error appear "Duck typing"
KIVY_IMPORTED = True
KIVY_IMPORT_MSG = """KvLint was not able import kivy module.
Please check if module is installed under currently used Kvlang: Python Path.
"""

try:
    from kivy.lang import Parser, ParserException # pylint: disable=unused-import
except ImportError:
    KIVY_IMPORTED = False
    class Parser(object):
        """Fake class when import can't be done of kivy module."""

        def __init__(self, content):
            """Fake initialization."""
            pass

    class ParserException(BaseException):
        """Fake class when import can't be done of kivy module."""

        pass
