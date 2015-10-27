# import logging

import logging

__author__ = 'jason'


class Logger:
    def __init__(self):
        pass

    @staticmethod
    def get_logger(name):
        logger = logging.getLogger(name)

        if not len(logger.handlers):
            logger.setLevel(logging.DEBUG)
            logger.propagate = False
            # now = datetime.datetime.now()
            # handler=logging.FileHandler('/root/credentials/Logs/ProvisioningPython'+ now.strftime("%Y-%m-%d") +'.log')
            # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            # handler.setFormatter(formatter)

            console = logging.StreamHandler()
            format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
            console.setFormatter(logging.Formatter(format_str))
            logger.addHandler(console)

        return logger
