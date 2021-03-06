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


# # A timer that will trigger and call stop on the scheduler
class MockRequestService(RequestorService):
    """
    Exists so that we can access mock requests that are setup by mock_requests.
    """
    def resolve_session(self):
        return mock_requests.create_mock_session()


class MockInitializerService(InitializerService):
    """
    Exists so that we can seed with mock data.
    """
    def seed_data(self):
        uri = "mock://github/events-quick-interval"
        timings = ResourceTimings()
        resource = Resource(uri, timings, json=True)
        self.db.save_resource(resource)
        self.log.debug("data seeded, entry count: [%d]." % self.db.resource_count())


class MockResponseService(ResponseParserService):
    """
    Exists so that we can mock the response parser to just dump back to the analyze
    queue.
    """
    def event_loop(self):
        while self.should_loop():
            self.log.info("TEST! - about to raise a manual test error - seeing this is good!")
            # <------------ raise an exception below!
            raise ServiceException("manual error - error 123 - seeing this is good!")


class MockErrorHandler(ErrorHandler):
    def __init__(self):
        ErrorHandler.__init__(self)

    def next(self, service_meta):
        self.log.error("ERROR HANDLER TEST! - %s" % service_meta.exceptions)
        return service_meta


def test_services_for_exceptions():
    """
    This test simulates the RuntimeError "maximum recursion depth exceeded".
    Ensure that this test passes without seeing this error.
    :return:
    """
    os = CannedOS("CannedOS")
    os.bootup()

    # == support services ==
    os.schedule_service(DBService, ServiceMetaData("database-service", recovery_enabled=True))
    os.schedule_service(QueueService, ServiceMetaData("queue-service", recovery_enabled=True))

    # == mock Init - will wait for analyzer to run ==
    os.schedule_service(MockInitializerService, ServiceMetaData("mock-initializer-service", recovery_enabled=True))

    os.schedule_service(AnalyzerService, ServiceMetaData("analyzer-service", recovery_enabled=True))

    # == freezes - will wait until analyzer runs ==
    os.schedule_service(Freezer50Service, ServiceMetaData("freezer-50", recovery_enabled=True))
    os.schedule_service(Freezer250Service, ServiceMetaData("freezer-250", recovery_enabled=True))
    os.schedule_service(Freezer500Service, ServiceMetaData("freezer-500", recovery_enabled=True))
    os.schedule_service(Freezer1000Service, ServiceMetaData("freezer-1000", recovery_enabled=True))

    # == error handlers for MockResponseService ==
    error_handlers = [MockErrorHandler]

    # == main services - in reverse order of execution so that
    #    analyzer runs last ==
    os.schedule_service(MockResponseService,
                        ServiceMetaData("mock-response-service", retries=2, recovery_enabled=True),
                        error_handlers=error_handlers)
    os.schedule_service(MockRequestService, ServiceMetaData("mock-requestor", recovery_enabled=True))

    # Manually restart a service to register a retry count of +1
    os.scheduler.restart_service("database-service")

    assert os.scheduler.get_services_count() == 10
    assert os.scheduler.get_service_manager().get_service_meta("database-service").starts == 1

    # now assert other services have retries set to 0
    assert os.scheduler.get_service_manager().get_service_meta("analyzer-service").starts == 0
    assert os.scheduler.get_service_manager().get_service_meta("mock-requestor").starts == 0
    assert os.scheduler.get_service_manager().get_service_meta("mock-initializer-service").starts == 0

    def stop_os():
        # by this time services have started and have registered retries == 1
        assert os.scheduler.get_service_manager().get_service_meta("analyzer-service").starts == 1
        assert os.scheduler.get_service_manager().get_service_meta("mock-requestor").starts == 1
        assert os.scheduler.get_service_manager().get_service_meta("mock-initializer-service").starts == 1

        # retry limit is set to 2, should only see three exceptions in the list
        # since it will start three times (initial start + two retries) and fail each time.
        assert len(os.scheduler.get_service_manager().get_service_meta("mock-response-service").exceptions) == 3

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

    assert os_greenlet.successful()
