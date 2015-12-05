# Lib
from v2.system.services import BaseService
from v2.data.processors.resource import ResourceAnalyzer

# System
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
    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        BaseService.__init__(self, name, parent_logger=parent_logger, enable_service_recovery=enable_service_recovery)
        self.analyzer = ResourceAnalyzer("resource-analyzer", parent_logger=self.log)
        self.queue = None

    def set_queue(self, queue):
        self.queue = queue

    def register(self):
        self.queue = self.get_directory_service_proxy().get_service("queue-service")

    def event_loop(self):
        """
        The event loop.
        """
        while True:
            # Don't do the below commented line, as the event loop will run fast
            # and will result in multiple lines being printed! Also that many of
            # log entries makes it confusing when narrowing down things. It is
            # better to tie a logging event to a logical event such as when a
            # resource may be requested (see below `can_request` method).
            # # don't do this -> self.log.debug("Size now: %d" % self.queue.analyzer_size())

            resource = self.queue.get_analyze()  # pop from queue

            if resource is not None:  # if an item exists
                # dirs = self.get_directory_service_proxy()

                if self.analyzer.can_request(resource):
                    size = self.queue.put_requests(resource)
                    self.log.debug("resource put on request queue, size: [%d]" % size)

            gevent.idle()
