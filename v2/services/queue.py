# Lib
from v2.system.services import BaseService
from v2.data.queue import BaseQueue, MemQueue

# System
import gevent

__author__ = 'jason'


class QueueService(BaseService, BaseQueue):
    """
    Queue service proxy.
    """

    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        BaseService.__init__(self, name, parent_logger=parent_logger, enable_service_recovery=enable_service_recovery)
        self.queue = MemQueue()  # queue implementation

    # below methods are proxies to the queue interface
    # -- Analyzer --
    def get_analyze(self):
        return self.queue.get_analyze()

    def put_analyze(self, item):
        return self.queue.put_analyze(item)

    def analyzer_size(self):
        return self.queue.analyzer_size()

    # -- Requestor --
    def put_requests(self, item):
        return self.queue.put_requests(item)

    def get_requests(self):
        return self.queue.get_requests()

    def requests_size(self):
        return self.queue.requests_size()

    def get_requests_error(self):
        return self.queue.get_requests_error()

    def put_requests_error(self, item):
        return self.queue.put_requests_error(item)

    def requests_error_size(self):
        return self.queue.requests_error_size()

    # -- Publish --
    def get_publish(self):
        return self.queue.get_publish()

    def put_publish(self, item):
        return self.queue.put_publish(item)

    def publish_size(self):
        return self.queue.publish_size()

    def get_publish_error(self):
        return self.queue.get_publish_error()

    def put_publish_error(self, item):
        return self.queue.put_publish_error(item)

    def publish_error_size(self):
        return self.queue.publish_error_size()