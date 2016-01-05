# External
import time
import gevent

# Lib
from v2.system.canned_os import CannedOS
from v2.services.freezer import Freezer50Service, Freezer250Service, Freezer500Service, Freezer1000Service
from v2.services.queue import QueueService
from v2.services.db import DBService
from v2.services.analyzer import AnalyzerService
from v2.services.error_handler import ErrorHandler, ErrorHandlerFactory
from v2.services.requestor import RequestorService
from v2.services.response import ResponseParserService
from v2.services.initializer import InitializerService
from v2.services.services import BaseService
from v2.data.timings import ResourceTimings
from v2.data.timings import Resource
from v2.data.simple_data import ServiceMetaData
from v2.system.exceptions import ServiceException

# Test libs
from tests.v2.system import mock_requests

# Global vars
worker_interval = .5
scheduler_interval = worker_interval + 1
os_stop_time = 10


class MockService(BaseService):
    """
    Mock service used to test delay was executed.
    """
    def __init__(self, name="base-service", parent_logger=None):
        BaseService.__init__(self, name, parent_logger=parent_logger)
        self.ack = False
        self.ack_time = None

    def should_loop(self):
        # run until ack is True or something external stops this service
        return self.ack is False

    def event_loop(self):
        while self.should_loop():
            self.ack = True
            self.ack_time = time.time()


class MockErrorHandler(ErrorHandler):
    def __init__(self):
        ErrorHandler.__init__(self)
        self.ack = False
        self.ack_time = None

    def next(self, service_meta):
        self.ack = True
        self.ack_time = time.time()
        self.log.info("TEST! - %s" % service_meta.exceptions)
        return service_meta


def test_with_delays():
    """
    This tests for service delays when starting. The service will delay start for 5
    seconds, and the os will stop in 10 seconds.
    :return:
    """
    os = CannedOS("CannedOS")
    os.bootup()

    # == services ==
    error_handlers = [MockErrorHandler]
    os.schedule_service(MockService,
                        ServiceMetaData("mock-service", delay=5, recovery_enabled=False),
                        error_handlers=error_handlers)

    # now assert services have retries set to 0
    assert os.scheduler.get_service_manager().get_service_meta("mock-service").starts == 0

    def stop_os():
        # by this time services have started and have registered retries == 1
        assert os.scheduler.get_service_manager().get_service_meta("mock-service").starts == 1
        assert os.scheduler.get_service_manager().get_service("mock-service").ack is True
        os.shutdown()

    # take timing from start to finish
    t1 = time.time()
    os_greenlet = gevent.spawn_later(os_stop_time, stop_os)
    gevent.joinall([os_greenlet])

    # == Test Validation/Verification ==
    # Makes sure that the test timer works correctly
    t2 = time.time()
    t3 = t2 - t1
    assert t3 > os_stop_time
    assert os_greenlet.successful()  # else look at the logs


def test_with_delay_that_never_starts():
    """
    This tests for service delays when starting but it won't ever start because
    the OS is scheduled to stop in 10 seconds, while the service start delay is
    set to start in 13 seconds (13 chosen because a time too close to the os
    stop of 10 like 11 might be too close on a very very slow system). On those
    systems operations take time, account for that. However anything past
    a couple seconds is not worth it.
    :return:
    """
    os = CannedOS("CannedOS")
    os.bootup()

    # == services ==
    error_handlers = [MockErrorHandler]
    os.schedule_service(MockService,
                        ServiceMetaData("mock-service", delay=13, recovery_enabled=False),
                        error_handlers=error_handlers)

    # now assert services have retries set to 0
    assert os.scheduler.get_service_manager().get_service_meta("mock-service").starts == 0

    def stop_os():
        # by this time services have started and have registered retries == 1
        meta = os.scheduler.get_service_manager().get_service_meta("mock-service")
        service = os.scheduler.get_service_manager().get_service("mock-service")

        assert meta.starts == 1

        # no exceptions occur as the system shutsdown before anything starts
        assert len(meta.exceptions) == 0

        assert service.ack is False

        os.shutdown()

    # take timing from start to finish
    t1 = time.time()
    os_greenlet = gevent.spawn_later(os_stop_time, stop_os)
    gevent.joinall([os_greenlet])

    # == Test Validation/Verification ==
    # Makes sure that the test timer works correctly
    t2 = time.time()
    t3 = t2 - t1
    assert t3 > os_stop_time

    # This os itself should not fail. Failed assertion will cause the os to fail.
    # The below is done because assertions in the greenlet will not raise outside
    # the gevent/greenlet scope.
    assert os_greenlet.successful()
