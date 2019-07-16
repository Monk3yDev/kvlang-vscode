"""Module store simple logging mechanism to the file."""
from __future__ import absolute_import
from time import gmtime, strftime

class Logger(object):
    """Simple logger for server troubleshooting purpose."""

    INFO = "INFO"
    MSG_CONTENT = "MSG_CONTENT"
    def __init__(self, file_name):
        """Initialize Logger."""
        self.file_name = file_name + ".log"
        self.debug_mode = False

    def log(self, log_type, msg):
        """Log specific type of message when debug mode is on."""
        if self.debug_mode:
            file = open(self.file_name, mode="a")
            file.write('[{}] ({}) msg="{}"\n'.format(strftime("%d.%m.%Y %H:%M:%S", gmtime()),
                                                     log_type, msg))
            file.close()

    def log_message(self, message):
        """Build and log message when debug mode is on."""
        if self.debug_mode:
            file = open(self.file_name, mode="a")
            info = '[{}] ({}) msg="{}"\n'.format(strftime("%d.%m.%Y %H:%M:%S", gmtime()),
                                                 self.MSG_CONTENT, "Header information")
            file.write(info)
            file.write("{}{}".format(message.build(), "\n"))
            file.close()

    def enable_debug_mode(self, argv):
        """Set debug mode if DEBUG_MODE arg exist in the argv list."""
        self.debug_mode = "DEBUG_MODE" in argv
        if self.debug_mode:
            self.log(self.INFO, "======= LOGGER INITIALIZED =======")
