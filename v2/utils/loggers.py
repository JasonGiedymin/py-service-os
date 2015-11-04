import logging
import sys

import structlog

__author__ = 'jason'


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


class Logger:
    def __init__(self):
        pass

    @staticmethod
    def get_logger(name):
        logger = structlog.getLogger().new(name=name)

        # if not len(logger.handlers):
        # if logger.hasHandlers():
        if logger._logger is not None:  # to prevent using n times
            if len(logger._logger.handlers) <= 0:
                logger.setLevel(logging.DEBUG)
                logger.propagate = False

                # now = datetime.datetime.now()
                # handler=logging.FileHandler('/root/credentials/Logs/ProvisioningPython'+ now.strftime("%Y-%m-%d") +'.log')
                # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
                # handler.setFormatter(formatter)

                console = logging.StreamHandler(sys.stdout)
                # format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
                # console.setFormatter(logging.Formatter(format_str))
                logger.addHandler(console)

        return logger
