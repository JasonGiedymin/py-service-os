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
timeout = 2  # if it doesn't start in 2 seconds, throw Exception
delay = 5
combined_time = timeout + delay


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


class MockServiceBad(BaseService):
    """
    Mock service used to test delay was executed.
    It will remain in the constructor for 20 seconds or be killed before
    that.
    """
    def __init__(self, name="base-service", parent_logger=None):
        BaseService.__init__(self, name, parent_logger=parent_logger)
        self.ack = False
        self.ack_time = None

    def start_event_loop(self):
        self.log.debug("mock event loop not starting, leaving in starting position for test.")
        return  # do nothing, state will remain in 'starting' position

    def should_loop(self):
        # run until ack is True or something external stops this service
        return self.ack is False

    def event_loop(self):
        """
        This method should never run because this mock class overrides the
        `start_event_loop` method.
        :return:
        """
        while self.should_loop():
            self.ack = True  # <-- if this code runs, this test is a failure!
            assert self.ack is False  # make sure this fails with an assert
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


def test_with_delays_and_timeout():
    """
    This tests for service delays when starting. The service will delay start for 5
    seconds, and after that a timeout of 2 seconds. It will however start just fine
    and will be successfull.
    :return:
    """
    os = CannedOS("CannedOS")
    os.bootup()

    # == services ==
    error_handlers = [MockErrorHandler]
    os.schedule_service(MockService,
                        ServiceMetaData("mock-service", delay=delay, start_timeout=timeout, recovery_enabled=False),
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
    This tests if the service started with a delay and if it timed out during the
    start within 2 seconds. The mock service being used has a sleep call for 5
    seconds that hopefully doesn't complete as another greenlet will remove
    the reference. This is effectively like a hard error killing off the greenlet
    reference. This shouldn't happen but if it does it should get picked up by the
    service manager. This test simulates that.
    :return:
    """
    os = CannedOS("CannedOS")
    os.bootup()

    # == services ==
    error_handlers = [MockErrorHandler]
    os.schedule_service(MockServiceBad,
                        ServiceMetaData("mock-service-bad", delay=1, start_timeout=2, recovery_enabled=False),
                        error_handlers=error_handlers)

    # now assert services have retries set to 0
    assert os.scheduler.get_service_manager().get_service_meta("mock-service-bad").starts == 0

    def stop_os():
        # by this time services have started and have registered retries == 1
        meta = os.scheduler.get_service_manager().get_service_meta("mock-service-bad")
        service = os.scheduler.get_service_manager().get_service("mock-service-bad")

        assert meta.starts == 1
        assert len(meta.exceptions) == 1
        assert service.ack is False

        os.shutdown()

    # take timing from start to finish
    t1 = time.time()
    os_greenlet = gevent.spawn_later(os_stop_time, stop_os)
    # remove_greenlet = gevent.spawn_later(2, remove_service)

    # gevent.joinall([os_greenlet, remove_greenlet])
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
