import time
import gevent

from system.os import Scheduler
from system.services import BaseService
from services.request import RequestSpec, RequestMachine, RequestMachineStates, RequestTimings, RequestService
from tests.system import mock_requests

__author__ = 'jason'


def test_request_service():
    timer_interval = 2

    class Timer(BaseService):
        """
        This test relies on this simple Timer
        to check things.
        """
        def __init__(self, service):
            BaseService.__init__(self, "timer")
            self.service = service

        def event_loop(self):
            self.log.debug("tick")
            gevent.sleep(timer_interval)
            self.service.stop()

    # setup scheduler
    scheduler = Scheduler("scheduler")
    assert scheduler is not None

    # create test support Timer class
    timer = Timer(scheduler)

    # setup request_service
    request_spec = RequestSpec(uri='mock://github/events')
    request_service = RequestService("request-service-1",
                                     request_spec,
                                     mock_requests.create_mock_session())
    assert request_service is not None

    # add services
    scheduler.add_service(request_service)

    # start services
    # scheduler.start()
    # gevent.joinall([scheduler.start()])  # blocks
    gevent.joinall([scheduler.start(), timer.start()])  # blocks

