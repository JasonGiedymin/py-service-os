# Lib
from v2.data.processors.resource import ResourceAnalyzer, ResourceStates
from v2.data.processors.timing_sorter import ResourceTimingSorter
from v2.services.services import BaseService

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
        self.timing_sorter = ResourceTimingSorter("timing-sorter", parent_logger=self.log)
        self.queue = None

    def register(self):
        self.queue = self.get_directory_service_proxy().get_service("queue-service")

    def _analyze_resource(self, resource):
        # dirs = self.get_directory_service_proxy()
        can_request, possible_state = self.analyzer.can_request(resource)
        if can_request:
            size = self.queue.put_requests(resource)
            self.log.debug("resource put on request queue, size: [%d]" % size)
        else:  # can't request because something is wrong or not ready
            # Optimization: check the state and if the state is interval time related
            # put the resource on the appropriate frozen queue. This will prevent
            # a high resolution event loop from always evaluating resources that are
            # known to not be ready until the far future
            # If a resource cannot be requested it is either waiting for a time vector,
            # or is in an error state. Time in this case is a vector because it's is an
            # interval (interval delta, or reset window delta)
            if possible_state in [ResourceStates.WaitingForReset, ResourceStates.WaitingForInterval]:
                self.timing_sorter.sort(resource, possible_state, self.queue)
            elif possible_state in [ResourceStates.EdgeError, ResourceStates.Error, ResourceStates.HasOwner]:
                size = self.queue.put_analyze_error(resource)
                self.log.debug("resource put back on analyze queue, size: [%d]" % size)

    def event_loop(self):
        """
        The event loop.
        """

        while self.should_loop():
            # Don't do the below commented line, as the event loop will run fast
            # and will result in multiple lines being printed! Also that many of
            # log entries makes it confusing when narrowing down things. It is
            # better to tie a logging event to a logical event such as when a
            # resource may be requested (see below `can_request` method).
            # # don't do this -> self.log.debug("Size now: %d" % self.queue.analyzer_size())

            resource = self.queue.get_analyze()  # pop from queue

            if resource is not None:  # if an item exists
                self._analyze_resource(resource)

            gevent.idle()
