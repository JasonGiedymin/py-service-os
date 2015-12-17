# External
import time
import gevent

# Lib
from v2.system.canned_os import CannedOS
from v2.services.freezer import Freezer50Service, Freezer250Service, Freezer500Service, Freezer1000Service
from v2.services.queue import QueueService
from v2.services.db import DBService
from v2.services.analyzer import AnalyzerService
from v2.services.requestor import RequestorService
from v2.services.response import ResponseParserService
from v2.services.initializer import InitializerService
from v2.data.timings import ResourceTimings
from v2.data.timings import Resource
from v2.data.simple_data import ServiceMetaData

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
            resource, response = self.queue.get_publish()  # pop from queue

            # try:
            if resource is not None and response is not None:  # if an item exists
                parse_success = self.response_parser.parse(response, resource)
                if parse_success:
                    self.log.debug("found resource, putting back on analyze queue (mock works)...")
                    self.queue.put_analyze(resource)
                else:
                    raise Exception("Error in MockResponseService - looks like bad parsing?")
            else:  # serious error if we got here
                raise Exception("Error in MockResponseService - looks like status was bad?")
            # except Exception as ex:
            #     print "Test error encountered - %s" % ex

            gevent.sleep(2)
            gevent.idle()


def test_freezer_services_for_max_recursion():
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

    # == freezes - will wait until analyzer runs ==
    os.schedule_service(Freezer50Service, ServiceMetaData("freezer-50", recovery_enabled=True))
    os.schedule_service(Freezer250Service, ServiceMetaData("freezer-250", recovery_enabled=True))
    os.schedule_service(Freezer500Service, ServiceMetaData("freezer-500", recovery_enabled=True))
    os.schedule_service(Freezer1000Service, ServiceMetaData("freezer-1000", recovery_enabled=True))

    # == main services - in reverse order of execution so that
    #    analyzer runs last ==
    os.schedule_service(MockResponseService, ServiceMetaData("mock-response-service", recovery_enabled=True))
    os.schedule_service(MockRequestService, ServiceMetaData("mock-requestor", recovery_enabled=True))
    os.schedule_service(AnalyzerService, ServiceMetaData("analyzer-service", recovery_enabled=True))

    assert os.scheduler.get_services_count() == 10

    def stop_os():
        os.shutdown()

    def stop():
        return gevent.spawn_later(os_stop_time, stop_os)

    # take timing from start to finish
    t1 = time.time()
    gevent.joinall([stop()])

    # == Test Validation/Verification ==
    # Makes sure that the test timer works correctly
    t2 = time.time()
    t3 = t2 - t1
    assert t3 > os_stop_time

