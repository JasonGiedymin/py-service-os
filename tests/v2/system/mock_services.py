import gevent

from v2.system.services import QueuedService, BaseStates, BaseService

__author__ = 'jason'


# A worker used for testing the scheduler
class TestWorker(BaseService):
    def __init__(self, name, loop_interval=.5):
        """
        Very important to note that this service has a loop interval of 500ms by default.
        :param name:
        :param loop_interval:
        :return:
        """
        BaseService.__init__(self, name)
        self.register_child_stat(name)
        self.loop_interval = loop_interval
        self.ack = False

    def event_loop(self):
        """
        Basic event loop that runs once with the specified interval
        :return:
        """
        while self.should_loop() and self.ack is False:
            gevent.sleep(self.loop_interval)
            output_service = self.get_directory_service_proxy().get_service("mock-output-service")

            output_service.put("test-worker-work-result")
            self.ack = True


class MockQueuedService(QueuedService):
    def __init__(self, quick_death=False, loop_interval=.750):
        """
        Very important to note that this service has a loop interval of 750ms by default.
        :param quick_death:
        :param loop_interval:
        :return:
        """
        name = "mock-output-service"
        QueuedService.__init__(self, name)
        self.register_child_stat(name)
        self.event_loop_ack = False
        self.quick_death = quick_death
        self.loop_interval = loop_interval

    def event_loop(self):
        while self.should_loop():
            gevent.sleep(self.loop_interval)
            self.log.debug("mock-output-service (really just MockQueuedService) doing some fake work...")

            if self.quick_death:
                self.event_loop_ack = True

            gevent.idle()
