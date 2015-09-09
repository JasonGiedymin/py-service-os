__author__ = 'jason'


import gevent

from system.services import OutputService, BaseStates, BaseService


# A worker used for testing the scheduler
class TestWorker(BaseService):
    def __init__(self, name, loop_interval=.5):
        BaseService.__init__(self, name)
        self.loop_interval = loop_interval

    def event_loop(self):
        while True:
            gevent.sleep(self.loop_interval)


class MockOutputService(OutputService):
    def __init__(self):
        OutputService.__init__(self, "mock-output-service")
        self.event_loop_ack = False

    def event_loop(self):
        gevent.sleep(.1)
        self.event_loop_ack = True
        # this service will stop as the end of the event loop has been reached
        self.set_state(BaseStates.Stopped)
        self.idle()
