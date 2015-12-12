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
    # -- Frozen 50 Queue --
    def get_frozen_50(self):
        return self.queue.get_frozen_50()

    def put_frozen_50(self, item):
        return self.queue.put_frozen_50(item)

    def frozen_50_size(self):
        return self.queue.frozen_50_size()

    # -- Frozen 250 Queue --
    def get_frozen_250(self):
        return self.queue.get_frozen_250()

    def put_frozen_250(self, item):
        return self.put_frozen_250(item)

    def frozen_250_size(self):
        return self.queue.frozen_250_size()

    # -- Frozen 500 Queue --
    def get_frozen_500(self):
        return self.queue.get_frozen_500()

    def put_frozen_500(self, item):
        return self.queue.put_frozen_500(item)

    def frozen_500_size(self):
        return self.queue.frozen_500_size()

    # -- Frozen 1000 Queue --
    def get_frozen_1000(self):
        return self.queue.get_frozen_1000()

    def put_frozen_1000(self, item):
        return self.queue.put_frozen_1000(item)

    def frozen_1000_size(self):
        return self.queue.frozen_1000_size()

    # -- Analyzer --
    def get_analyze(self):
        return self.queue.get_analyze()

    def put_analyze(self, item):
        return self.queue.put_analyze(item)

    def analyze_size(self):
        return self.queue.analyze_size()

    def get_analyze_error(self):
        return self.queue.get_analyze_error()

    def put_analyze_error(self, item):
        return self.queue.put_analyze_error(item)

    def analyze_error_size(self):
        return self.queue.analyze_error_size()

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