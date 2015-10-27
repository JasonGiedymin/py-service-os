from tests.system import mock_requests
from v2.data.timings import ResourceTimings
from v2.data.timings import Resource
from v2.data.processors.response_parser import ResponseParser

__author__ = 'jason'


def test_response_parser():
    uri = "mock://github/events"

    session = mock_requests.create_mock_session()
    response = session.get(uri)
    timings = ResourceTimings()
    resource = Resource(uri, timings)

    # parse out timings from headers
    # don't worry about getting the body to publish,
    # that is something the service should worry about
    parser = ResponseParser("response-parser")
    parser.parse(response, resource)

    # asserts new timings
    assert timings.interval == int(mock_requests.GLOBAL_MOCK_REQUEST_INTERVAL)
    assert timings.rate_limit == int(mock_requests.GLOBAL_MOCK_REQUEST_RATELIMIT)
    assert timings.rate_limit_remaining == int(mock_requests.GLOBAL_MOCK_REQUEST_REMAINING)
    assert timings.etag == mock_requests.GLOBAL_MOCK_REQUEST_ETAG1
    assert timings.time_to_reset == int(mock_requests.GLOBAL_MOCK_REQUEST_RESET) * 1000