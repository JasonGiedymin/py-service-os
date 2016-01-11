from v2.data.timings import ResourceTimings, ResourceHeaders, Resource
from v2.data.processors.resource import ResourceAnalyzer
from v2.utils import timeutils
from v2.data.states import ResourceStates

__author__ = 'jason'


def test_resource_analyzer_edge_case():
    timings = ResourceTimings()  # default timings
    timings.rate_limit_remaining = 0  # limit reached
    timings.time_to_reset = timeutils.milliseconds() - 2000  # past now
    timings.last_request_timestamp = timeutils.milliseconds() - 1000  # was done after reset

    resource = Resource("mock://test", timings, ResourceHeaders())
    ra = ResourceAnalyzer("test-resource-analyzer")

    assert ra.is_edge_case(resource)
    assert ra.can_request(resource) == (False, ResourceStates.EdgeError)


def test_resource_with_owner():
    """
    Scenario: resource has an owner.
    """
    timings = ResourceTimings()  # default timings
    timings.rate_limit_remaining = 1000
    timings.time_to_reset = timeutils.milliseconds() - 2000  # past now
    timings.last_request_timestamp = timeutils.milliseconds() - 1000  # was done after reset

    resource = Resource("mock://test", timings, ResourceHeaders(), owner="TestProcessor")
    ra = ResourceAnalyzer("test-resource-analyzer")

    assert ra.can_request(resource) == (False, ResourceStates.HasOwner)


def test_with_limit_remaining():
    """
    Scenario: limit is 1000.
    should be able to request.
    """
    timings = ResourceTimings()  # default timings
    timings.rate_limit_remaining = 1000
    timings.time_to_reset = timeutils.milliseconds() - 2000  # past now
    timings.last_request_timestamp = timeutils.milliseconds() - 1000  # was done after reset

    resource = Resource("mock://test", timings, ResourceHeaders())
    ra = ResourceAnalyzer("test-resource-analyzer")

    assert ra.can_request(resource)


def test_limit_reached_reset_ready():
    """
    Scenario: limit is 0, with time_to_reset passed
    Should be able to request.
    """
    timings = ResourceTimings()  # default timings
    timings.rate_limit_remaining = 0
    timings.time_to_reset = timeutils.milliseconds() - 2000  # in the past
    # timings.last_request_timestamp = timeutils.milliseconds() - 1000  # was done after reset

    resource = Resource("mock://test", timings, ResourceHeaders())
    ra = ResourceAnalyzer("test-resource-analyzer")

    assert ra.can_request(resource) == (True, None)


def test_limit_reached_reset_infuture():
    """
    Scenario: limit is 0, with time_to_reset in the future.
    Should not be able to request.
    """
    timings = ResourceTimings()  # default timings
    timings.rate_limit_remaining = 0
    timings.time_to_reset = timeutils.milliseconds() + 2000  # in the future

    resource = Resource("mock://test", timings, ResourceHeaders())
    ra = ResourceAnalyzer("test-resource-analyzer")

    assert ra.can_request(resource) == (False, ResourceStates.WaitingForReset)


def test_waiting_for_interval():
    """
    Scenario: limit is 0, with time_to_reset in the future.
    Should not be able to request.
    """
    timings = ResourceTimings()  # default timings
    timings.rate_limit_remaining = 1000
    timings.time_to_reset = timeutils.milliseconds() + 2000  # in the future
    timings.update_timestamp()
    timings.update_interval_timestamp()
    timings.interval = 10000

    resource = Resource("mock://test", timings, ResourceHeaders())
    ra = ResourceAnalyzer("test-resource-analyzer")

    assert ra.can_request(resource) == (False, ResourceStates.WaitingForInterval)
