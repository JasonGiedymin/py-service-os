from v2.system.services import BaseService
from v2.data.processors.timing_sorter import ResourceTimingSorter
from v2.data.timings import ResourceTimings, Resource
from v2.data.states import ResourceStates
from v2.utils import timeutils

from tests.v2.system import mock_requests

import gevent


class MockQueueService(BaseService):
    def __init__(self, name):
        BaseService.__init__(self, name, parent_logger=None, enable_service_recovery=False)
        self.f1000_calls = 0
        self.f500_calls = 0
        self.f250_calls = 0
        self.f50_calls = 0
        self.fa_calls = 0

    def put_frozen_50(self, resource):
        # self.log.info("mock-queue.put_frozen_50() called with resource: [%s]" % resource)
        self.f50_calls += 1

    def put_frozen_250(self, resource):
        # self.log.info("mock-queue.put_frozen_250() called with resource: [%s]" % resource)
        self.f250_calls += 1

    def put_frozen_500(self, resource):
        # self.log.info("mock-queue.put_frozen_500() called with resource: [%s]" % resource)
        self.f500_calls += 1

    def put_frozen_1000(self, resource):
        # self.log.info("mock-queue.put_frozen_1000() called with resource: [%s]" % resource)
        self.f1000_calls += 1

    def put_analyze(self, resource):
        self.log.info("mock-queue.put_analyze() called with resource: [%s]" % resource)
        self.fa_calls += 1


def test_resource_timing_sorter():
    mock_queue = MockQueueService("mock-queue")  # mock queue
    uri = "mock://github/events-quick-interval"  # create mock resource

    # create resource
    timings = ResourceTimings()
    resource = Resource(uri, timings, json=True)

    # get mock response
    session = mock_requests.create_mock_session()
    response = session.get(uri)

    resource.timings.update(response, resource.headers)

    # modify interval timing directly and make it trigger
    # in the future
    resource.timings.interval = 2000
    resource.timings.update_timestamp
    resource.timings.update_interval_timestamp()

    sorter = ResourceTimingSorter("test-sorter")
    sorter.sort(resource, ResourceStates.WaitingForInterval, mock_queue)

    def work():
        for n in range(25):
            sorter.sort(resource, ResourceStates.WaitingForInterval, mock_queue)
            gevent.sleep(.10)

    work()

    # sometimes depending on the test runner or machine, things will be slow.
    # rather than assert on very specific timings, just ensure the counters
    # were hit
    assert mock_queue.f1000_calls >= 1
    assert mock_queue.f500_calls >= 1
    assert mock_queue.f250_calls >= 1
    assert mock_queue.f50_calls >= 1
    assert mock_queue.fa_calls >= 1
