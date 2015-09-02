__author__ = 'jason'

from gevent.queue import Queue


class RoundRobinIndexer:
    def __init__(self, n):
        if n <= 1:
            raise Exception("RoundRobinIndexer count must be > 1")

        self.queue = Queue(maxsize=n)

        for i in range(0, n):
            self.queue.put(i)

    def next(self):
        value = self.queue.get()
        self.queue.put(value)
        return value
