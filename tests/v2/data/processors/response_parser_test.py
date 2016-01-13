from tests.v2.system import mock_requests
import v2.data.timings as timingslib
from v2.data.timings import ResourceTimings
from v2.data.timings import Resource
from v2.data.processors.response_parser import ResponseParser

import requests

__author__ = 'jason'


def test_response_parser():
    """
    This test will execute a mock request with mock results.
    :return:
    """
    uri = "mock://github/events/statustest"

    session = mock_requests.create_mock_session()
    response = session.get(uri)
    timings = ResourceTimings()
    resource = Resource(uri, timings, json=True)

    # parse out timings from headers
    # don't worry about getting the body to publish,
    # that is something the service should worry about
    parser = ResponseParser("response-parser")
    parser.parse(response, resource)

    # asserts new timings
    assert timings.interval == int(mock_requests.GLOBAL_MOCK_REQUEST_INTERVAL) * 1000
    assert timings.rate_limit == int(mock_requests.GLOBAL_MOCK_REQUEST_RATELIMIT)
    assert timings.rate_limit_remaining == int(mock_requests.GLOBAL_MOCK_REQUEST_REMAINING)
    assert timings.etag == mock_requests.GLOBAL_MOCK_REQUEST_ETAG1
    assert timings.time_to_reset == int(mock_requests.GLOBAL_MOCK_REQUEST_RESET) * 1000


def test_without_header_values():
    """
    This test will execute a mock request with mock results. The results
    however will contain a response no values for certain header keys.
    This demonstrates that defaults will be used in the absense of
    keys which would have been parsed out from the response and used in
    calculating new timings.
    :return:
    """
    uri = "mock://somedomain/withoutheaders"

    session = mock_requests.create_mock_session()
    response = session.get(uri)
    timings = ResourceTimings()
    resource = Resource(uri, timings, json=True)

    # parse out timings from headers
    # don't worry about getting the body to publish,
    # that is something the service should worry about
    parser = ResponseParser("response-parser")
    parser.parse(response, resource)

    # asserts new timings (note that a lot of these are in ms so they must be calculated)
    assert timings.interval == timingslib.DEFAULT_INTERVAL * 1000
    assert timings.rate_limit == timingslib.DEFAULT_RATE_LIMIT
    assert timings.rate_limit_remaining == timingslib.DEFAULT_RATE_LIMIT_REMAINING
    assert timings.etag == mock_requests.GLOBAL_MOCK_REQUEST_ETAG1
    assert timings.time_to_reset == timingslib.DEFAULT_TIME_TO_RESET * 1000


def test_real_resource():
    """
    This test will execute a live test against Google. The response
    will then be parsed for timing information (of which there will
    be none).
    calculating new timings.
    :return:
    """
    uri = "http://google.com"

    session = requests.Session()
    response = session.get(uri)

    # live request must return!
    assert response.status_code == 200

    timings = ResourceTimings()
    resource = Resource(uri, timings, json=False)

    # parse out timings from headers
    # don't worry about getting the body to publish,
    # that is something the service should worry about
    parser = ResponseParser("response-parser")
    parser.parse(response, resource)

    # google returns none of these values
    assert timings.interval == timingslib.DEFAULT_INTERVAL * 1000
    assert timings.rate_limit == timingslib.DEFAULT_RATE_LIMIT
    assert timings.rate_limit_remaining == timingslib.DEFAULT_RATE_LIMIT_REMAINING
    assert timings.etag == ''  # google has no etag
    assert timings.time_to_reset == timingslib.DEFAULT_TIME_TO_RESET * 1000
