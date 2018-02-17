""" Utils module store variables and function used in
    cross platform systems"""
import os

EOL_POSIX = '\r\n'
EOL_WIN = '\n'
EOL = EOL_WIN if os.name != "posix" else EOL_POSIX
CHARSET = "utf-8"
