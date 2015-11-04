from v2.utils.loggers import Logger


__author__ = 'jason'


class DataProcessor:
    def __init__(self, name, parent_logger=None):
        if parent_logger is None:
            self.name = "processor/%s" % name
            self.log = Logger.get_logger(self.name)
        else:
            # self.log = parent_logger.getChild(name)

            parent_name = parent_logger._context["name"]
            self.name = "%s/%s" % (parent_name, name)
            self.log = parent_logger.new(name=self.name)
