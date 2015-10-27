from v2.utils.loggers import Logger


__author__ = 'jason'


class Processor:
    def __init__(self, name):
        self.name = "processor/%s" % name
        self.log = Logger.get_logger(self.name)
