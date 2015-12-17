from gevent.queue import Queue
from abc import ABCMeta, abstractmethod

__author__ = 'jason'


class BaseQueue(object):
    __metaclass__ = ABCMeta

    # -- Frozen 50 Queue --
    @abstractmethod
    def get_frozen_50(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_frozen_50(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def frozen_50_size(self):
        raise NotImplementedError("Please Implement this method")

    # -- Frozen 250 Queue --
    @abstractmethod
    def get_frozen_250(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_frozen_250(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def frozen_250_size(self):
        raise NotImplementedError("Please Implement this method")

    # -- Frozen 500 Queue --
    @abstractmethod
    def get_frozen_500(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_frozen_500(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def frozen_500_size(self):
        raise NotImplementedError("Please Implement this method")

    # -- Frozen 1000 Queue --
    @abstractmethod
    def get_frozen_1000(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_frozen_1000(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def frozen_1000_size(self):
        raise NotImplementedError("Please Implement this method")

    # -- Analyzer --
    @abstractmethod
    def get_analyze(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_analyze(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def analyze_size(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def get_analyze_error(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_analyze_error(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def analyze_error_size(self):
        raise NotImplementedError("Please Implement this method")

    # -- Requestor --
    @abstractmethod
    def get_requests(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_requests(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def requests_size(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def get_requests_error(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_requests_error(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def requests_error_size(self):
        raise NotImplementedError("Please Implement this method")

    # -- Publish --
    @abstractmethod
    def get_publish(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_publish(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def publish_size(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def get_publish_error(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_publish_error(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def publish_error_size(self):
        raise NotImplementedError("Please Implement this method")


class MemQueue(BaseQueue):
    """
    This is a basic in memory queue that can be used knowing
    that it is not persistent. Good for tests.
    """

    def __init__(self):
        self.data = {
            "topics": {
                "frozen-50": Queue(), # red and write in 50ms intervals
                "frozen-250": Queue(),  # read and write in 250ms intervals
                "frozen-500": Queue(),  # read and write in 500ms intervals
                "frozen-1000": Queue(),  # read and write in 1000ms (1s) intervals
                "analyze": Queue(),
                "analyze-errors": Queue(),
                "requests": Queue(),
                "request-errors": Queue(),
                "publish": Queue(),
                "publish-errors": Queue()
            },
            "metrics": {}
        }

        # aliases for the data dict above
        # frozen queues
        self.frozen_50 = self.data["topics"]["frozen-50"]
        self.frozen_250 = self.data["topics"]["frozen-250"]
        self.frozen_500 = self.data["topics"]["frozen-500"]
        self.frozen_1000 = self.data["topics"]["frozen-1000"]

        self.analyze = self.data["topics"]["analyze"]
        self.analyze_errors = self.data["topics"]["analyze-errors"]
        self.requests = self.data["topics"]["requests"]
        self.request_errors = self.data["topics"]["request-errors"]
        self.publish = self.data["topics"]["publish"]
        self.publish_errors = self.data["topics"]["publish-errors"]

    # -- Frozen 50 Queue --
    def get_frozen_50(self):
        return self.frozen_50.get()

    def put_frozen_50(self, item):
        self.frozen_50.put(item)
        return self.frozen_50.qsize()

    def frozen_50_size(self):
        return self.frozen_50.qsize()

    # -- Frozen 250 Queue --
    def get_frozen_250(self):
        return self.frozen_250.get()

    def put_frozen_250(self, item):
        self.frozen_250.put(item)
        return self.frozen_250.qsize()

    def frozen_250_size(self):
        return self.frozen_250.qsize()

    # -- Frozen 500 Queue --
    def get_frozen_500(self):
        return self.frozen_500.get()

    def put_frozen_500(self, item):
        self.frozen_500.put(item)
        return self.frozen_500.qsize()

    def frozen_500_size(self):
        return self.frozen_500.qsize()

    # -- Frozen 1000 Queue --
    def get_frozen_1000(self):
        return self.frozen_1000.get()

    def put_frozen_1000(self, item):
        self.frozen_1000.put(item)
        return self.frozen_1000.qsize()

    def frozen_1000_size(self):
        return self.frozen_1000.qsize()

    # -- Analyzer --
    def get_analyze(self):
        return self.analyze.get()

    def put_analyze(self, item):
        self.analyze.put(item)
        return self.analyze.qsize()

    def analyze_size(self):
        return self.analyze.qsize()

    def get_analyze_error(self):
        return self.analyze_errors.get()

    def put_analyze_error(self, item):
        self.analyze_errors.put(item)
        return self.analyze_errors.qsize()

    def analyze_error_size(self):
        return self.analyze_errors.qsize()

    # -- Requestor --
    def get_requests(self):
        """
        Get a single item from the request queue.
        :return:
        """
        return self.requests.get()

    def put_requests(self, item):
        self.requests.put(item)
        return self.requests.qsize()

    def requests_size(self):
        return self.requests.qsize()

    def get_requests_error(self):
        return self.request_errors.get()

    def put_requests_error(self, item):
        self.request_errors.put(item)
        return self.request_errors.qsize()

    def requests_error_size(self):
        return self.request_errors.qsize()

    # -- Publish --
    def get_publish(self):
        return self.publish.get()

    def put_publish(self, item):
        self.publish.put(item)
        return self.publish.qsize()

    def publish_size(self):
        return self.publish.qsize()

    def get_publish_error(self):
        return self.publish_errors.get()

    def put_publish_error(self, item):
        self.publish_errors.put(item)
        return self.publish_errors.qsize()

    def publish_error_size(self):
        return self.publish_errors.qsize()
