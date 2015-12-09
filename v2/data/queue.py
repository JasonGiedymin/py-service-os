from gevent.queue import Queue
from abc import ABCMeta, abstractmethod

__author__ = 'jason'


class BaseQueue(object):
    __metaclass__ = ABCMeta

    # -- Analyzer --
    @abstractmethod
    def get_analyze(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def put_analyze(self, item):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def analyzer_size(self):
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
                "analyze": Queue(),
                "requests": Queue(),
                "request-errors": Queue(),
                "publish": Queue(),
                "publish-errors": Queue()
            },
            "metrics": {}
        }

        # alaises for the data dict above
        self.analyze = self.data["topics"]["analyze"]
        self.requests = self.data["topics"]["requests"]
        self.request_errors = self.data["topics"]["request-errors"]
        self.publish = self.data["topics"]["publish"]
        self.publish_errors = self.data["topics"]["publish-errors"]

    # -- Analyzer --
    def get_analyze(self):
        return self.analyze.get()

    def put_analyze(self, item):
        self.analyze.put(item)
        return self.analyze.qsize()

    def analyzer_size(self):
        return self.analyze.qsize()

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
