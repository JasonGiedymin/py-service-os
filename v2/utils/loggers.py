import logging
import sys

import structlog

__author__ = 'jason'


# structlog.stdlib.TRACE = TRACE = 5
# structlog.stdlib._NAME_TO_LEVEL['trace'] = TRACE
# logging.addLevelName(TRACE, "TRACE")


# class TraceableLogger(structlog.BoundLoggerBase):
#     def trace(self, event=None, **event_kw):
#         args, kw = self._process_event('trace', event, event_kw)
#         return getattr(self._logger, 'trace')(*args, **kw)
#
#     def warn(self, event, **kw):
#         return self._proxy_to_logger('warn', event, **kw)
#
#     def error(self, event, **kw):
#         return self._proxy_to_logger('error', event, **kw)
#
#     def debug(self, event, **kw):
#         return self._proxy_to_logger('debug', event, **kw)
#
#     def info(self, event, **kw):
#         return self._proxy_to_logger('info', event, **kw)

structlog.configure_once(
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
    # wrapper_class=TraceableLogger,
    cache_logger_on_first_use=True,
)


class Logger:
    def __init__(self):
        pass

    @staticmethod
    def get_logger(name):
        logger = structlog.get_logger().new(name=name)

        if logger._logger is not None:  # to prevent using n times
            if len(logger._logger.handlers) <= 0:

                # logger._logger.setLevel(TRACE)
                logger.setLevel(logging.DEBUG)
                # logger.setLevel(logging.INFO)

                logger.propagate = False
                console = logging.StreamHandler(sys.stdout)
                logger._logger.addHandler(console)

        return logger
