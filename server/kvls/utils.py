"""Utils module store variables and function used in cross platform systems."""
from __future__ import absolute_import
import os

EOL_POSIX = '\n'
EOL_WIN = '\r\n'
EOL = EOL_WIN if os.name != "posix" else EOL_POSIX

EOL_LSP_POSIX = '\r\n'
EOL_LSP_WIN = '\n'
EOL_LSP = EOL_LSP_WIN if os.name != "posix" else EOL_LSP_POSIX

CHARSET = "utf-8"
