""" Module store simple logging mechanism to the file """

class Logger(object):
    """ Simple logger for only use in production code or during
        troubleshooting. """
    INFO = "INFO"
    DISABLED = False
    def __init__(self, file_name="Logger.txt"):
        self.file_name = file_name
        self.__clear()

    def log(self, log_type, msg):
        """ Log specific type of message """
        if self.DISABLED is False:
            file = open(self.file_name, mode="a")
            file.write("[{}] {} \n".format(log_type, msg))
            file.close()

    def __clear(self):
        """ Remove old file if exist and create new one """
        if self.DISABLED is False:
            file = open(self.file_name, mode="w")
            file.close()