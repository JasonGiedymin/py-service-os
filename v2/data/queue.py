from gevent.queue import Queue

__author__ = 'jason'


class MemQueue:
    """
    This is a basic in memory queue that can be used for testing.
    It is not persistent.
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

    def get_analyze(self):
        return self.analyze.get()

    def put_analyze(self, item):
        self.analyze.put(item)
        return self.analyze.qsize()

