__author__ = 'jason'

import gevent

from states import BaseStates


class BaseService:
    def event_loop(self):
        """
        Override
        """
        pass

    def __init__(self, name="base-service"):
        print "%s - Init" % name
        self.name = name
        self.greenlet = None
        self.service_state = BaseStates.Idle

    def start(self):
        print "%s - Starting..." % self.name
        self.greenlet = gevent.spawn(self.event_loop)
        self.service_state = BaseStates.Started
        return self.greenlet

    def stop(self):
        print "%s - Stopping..." % self.name
        gevent.kill(self.greenlet)
        self.service_state = BaseStates.Stopped


class TestWorker(BaseService):
    def __init__(self, name):
        BaseService.__init__(self, name)
        # self.name = "test-worker-1"

    def event_loop(self):
        while True:
            print "%s - working" % self.name
            gevent.sleep(.5)


class RequestSpec:
    def __init__(self):
        pass


class RequestWorker:
    # do work
    # take requestspec
    def __init__(self, spec):
        self.spec = spec
        self.greenlet = None
        self.on = False

    def work(self):
        while self.on:
            print("Working on http request")
            gevent.sleep(1)

    def start(self):
        print "starting..."
        self.on = True
        self.greenlet = gevent.spawn(self.work)
        return self.greenlet

    def stop(self):
        self.on = False
        print "<- Stopped!"
        gevent.kill(self.greenlet)

# w = RequestWorker(RequestSpec())
# gevent.spawn_later(10, w.stop)
# gevent.joinall([w.start()])
