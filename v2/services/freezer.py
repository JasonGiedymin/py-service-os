# Lib
from v2.data.processors.resource import ResourceAnalyzer, ResourceStates
from v2.data.processors.timing_sorter import ResourceTimingSorter
from v2.services.services import BaseService

# System
from abc import abstractmethod
import gevent

__author__ = 'jason'


class FreezerService(BaseService):
    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        BaseService.__init__(self, name, parent_logger=parent_logger, enable_service_recovery=enable_service_recovery)
        self.analyzer = ResourceAnalyzer("resource-analyzer", parent_logger=self.log)
        self.timing_sorter = ResourceTimingSorter("timing-sorter", parent_logger=self.log)
        self.queue = None
        self.sleep_time = .05  # 50 (.05), 250 (.25), 500 (.5), 1000 (1)

    def register(self):
        self.queue = self.get_directory_service_proxy().get_service("queue-service")

    @abstractmethod
    def get_resource(self):
        """
        Use self.queue to get the resource in the implementation
        :return:
        """
        raise NotImplementedError("Please Implement this method")

    def _analyze_resource(self, resource):
        can_request, possible_state = self.analyzer.can_request(resource)

        if can_request:
            # size = self.put_resource(resource)
            size = self.queue.put_requests(resource)
            self.log.debug("resource put on request queue, size: [%d]" % size)
        else:
            if possible_state in [ResourceStates.WaitingForReset, ResourceStates.WaitingForInterval]:
                self.timing_sorter.sort(resource, possible_state, self.queue)
            elif possible_state in [ResourceStates.EdgeError, ResourceStates.Error, ResourceStates.HasOwner]:
                size = self.queue.put_analyze_error(resource)
                self.log.debug("resource put back on analyze queue, size: [%d]" % size)

    def event_loop(self):
        while self.should_loop():
            resource = self.get_resource()

            if resource is not None:  # if an item exists
                self._analyze_resource(resource)

            # In future revisions when I make use of real multi-threading this concept
            # will be realized. In terms of gevent, sleep is idle but with a greenlet waiting
            # for a scheduled time. So the below if still using gevent, does nothing but prevent
            # logging statements from running.
            gevent.sleep(self.sleep_time)  # in terms of gevent this is just a yield with a waiter
            gevent.idle()  # being a very good citizen, we yield again


class Freezer50Service(FreezerService):
    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        FreezerService.__init__(self, name, parent_logger=parent_logger,
                                enable_service_recovery=enable_service_recovery)
        self.sleep_time = .05

    def get_resource(self):
        return self.queue.get_frozen_50()


class Freezer250Service(FreezerService):
    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        FreezerService.__init__(self, name, parent_logger=parent_logger,
                                enable_service_recovery=enable_service_recovery)
        self.sleep_time = .25

    def get_resource(self):
        # raise Exception
        return self.queue.get_frozen_250()


class Freezer500Service(FreezerService):
    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        FreezerService.__init__(self, name, parent_logger=parent_logger,
                                enable_service_recovery=enable_service_recovery)
        self.sleep_time = .5

    def get_resource(self):
        return self.queue.get_frozen_500()


class Freezer1000Service(FreezerService):
    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        FreezerService.__init__(self, name, parent_logger=parent_logger,
                                enable_service_recovery=enable_service_recovery)
        self.sleep_time = 1

    def get_resource(self):
        return self.queue.get_frozen_1000()
