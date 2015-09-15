__author__ = 'jason'

from services.request import RequestSpec, RequestMachineStates, RequestTimings
from tests.system import mock_requests


def test_request_timings():
    request_spec = RequestSpec(uri='mock://github/events')

    # get mock session and do a get
    session = mock_requests.create_mock_session()
    resp = session.get(request_spec.uri)

    # default timings
    timings = RequestTimings(request_spec)

    # assert defaults
    assert timings.interval == '1'
    assert timings.rate_limit == '1'
    assert timings.rate_limit_remaining == '1'
    assert timings.time_to_reset == '60'

    # update timings
    timings.update(resp)

    # asserts new timings
    assert timings.interval == mock_requests.GLOBAL_MOCK_REQUEST_INTERVAL
    assert timings.rate_limit == mock_requests.GLOBAL_MOCK_REQUEST_RATELIMIT
    assert timings.rate_limit_remaining == mock_requests.GLOBAL_MOCK_REQUEST_REMAINING
    assert timings.time_to_reset == mock_requests.GLOBAL_MOCK_REQUEST_RESET


def test_mock_request_machine():
    # init
    request_spec = RequestSpec(uri='mock://github/events')
    machine = mock_requests.create_mock_request_machine(request_spec)
    assert machine is not None
    assert machine.state == RequestMachineStates.Idle

    # get data
    resp = machine.get()
    assert resp is not None

    # check latency stats
    assert machine.latency is not None
    assert machine.latency.data.get('count') == 1

    # check latency window stats
    assert machine.latency_window is not None
    assert machine.latency_window.data.get('count') == 1

    # check timings, that update was called and working correctly
    assert machine.timings.interval == mock_requests.GLOBAL_MOCK_REQUEST_INTERVAL
    assert machine.timings.rate_limit == mock_requests.GLOBAL_MOCK_REQUEST_RATELIMIT
    assert machine.timings.rate_limit_remaining == mock_requests.GLOBAL_MOCK_REQUEST_REMAINING
    assert machine.timings.time_to_reset == mock_requests.GLOBAL_MOCK_REQUEST_RESET

    for x in range(0, 99):
        machine.get()

    assert machine.latency.data.get('count') == 100
    assert machine.latency_window.data.get('count') == 100

    print machine.latency.data
# on first call flag
# set limits based on resp

