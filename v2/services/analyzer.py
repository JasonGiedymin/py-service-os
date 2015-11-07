# Lib
from v2.system.services import BaseService

# System
from uuid import uuid4
import gevent

__author__ = 'jason'


class AnalyzerService(BaseService):
    """
    The Analyzer service is the process which will handle the analysis
    of resources (type Resource) and determine whether or not they
    warrant a request. Upon passing the necessary checks the service
    will send the resource to the next queue, or to the error queue.

    By this nature this service uses the BaseService class which
    within itself composities a greenlet.
    """
    def __init__(self, name, parent_logger=None):
        BaseService.__init__(self, name, parent_logger=parent_logger)

    def event_loop(self):
        """
        The event loop.
        """
        while True:
            self.log.debug("workin the URIs")
            gevent.sleep(1)
