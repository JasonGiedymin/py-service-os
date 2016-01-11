import gevent

from system.services import OutputService, BaseStates, BaseService

__author__ = 'jason'


# A worker used for testing the scheduler
class TestWorker(BaseService):
    def __init__(self, name, loop_interval=.5):
        BaseService.__init__(self, name)
        self.register_child_stat(name)
        self.loop_interval = loop_interval
        self.ack = False

    def event_loop(self):
        """
        Basic event loop that runs once with the specified interval
        :return:
        """
        while self.ack is False:
            gevent.sleep(self.loop_interval)
            output_service = self.get_directory_service_proxy().get_service("mock-output-service")
            output_service.put("test-worker-work-result")
            self.ack = True


class MockOutputService(OutputService):
    def __init__(self):
        name = "mock-output-service"
        OutputService.__init__(self, name)
        self.register_child_stat(name)
        self.event_loop_ack = False

    def event_loop(self):
        gevent.sleep(.1)
        self.event_loop_ack = True
        # this service will stop as the end of the event loop has been reached
        self.set_state(BaseStates.Stopped)
        self.idle()
