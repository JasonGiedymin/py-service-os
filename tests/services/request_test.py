import time
import gevent

from services.request import RequestSpec, RequestMachine, RequestMachineStates, RequestTimings
from utils import timeutils
from tests.system import mock_requests

__author__ = 'jason'


def test_request_timings():
    send_headers = {
        'token': '0000000000'
    }

    request_spec = RequestSpec(uri='mock://github/events', send_headers=send_headers)

    # get mock session and do a get
    session = mock_requests.create_mock_session()
    resp = session.get(request_spec.uri)

    # default timings
    timings = RequestTimings(request_spec)

    # assert defaults
    assert timings.interval == '1000'
    assert timings.rate_limit == '1'
    assert timings.rate_limit_remaining == '1'
    assert timings.time_to_reset == '60'
    assert timings.etag is None

    # update timings
    timings.update(resp)

    # asserts new timings
    assert timings.interval == mock_requests.GLOBAL_MOCK_REQUEST_INTERVAL
    assert timings.rate_limit == mock_requests.GLOBAL_MOCK_REQUEST_RATELIMIT
    assert timings.rate_limit_remaining == mock_requests.GLOBAL_MOCK_REQUEST_REMAINING
    assert timings.time_to_reset == mock_requests.GLOBAL_MOCK_REQUEST_RESET


def test_can_request():
    """
    This test tests against the internals and calls can_request
    directly.
    :return:
    """

    # for simplicity we set interval to 1
    request_spec = RequestSpec(uri='mock://github/events/limits')
    machine = mock_requests.create_mock_request_machine(request_spec)

    # start modifying
    machine.timings.rate_limit_remaining = '0'
    # set last timestamp to 60 seconds ago
    machine.timings.last_request_timestamp = timeutils.milliseconds() - 60000
    # time to reset window will be now + 1 seconds
    machine.timings.time_to_reset = str(timeutils.milliseconds() + 1000)
    # limit from above should be 0, check to see if the window has passed
    assert machine.can_request() == (False, RequestMachineStates.WaitingForReset)
    # sleep one second, allowing reset window to pass, allowing call
    gevent.sleep(2)  # ensures that we really went past the reset above of +1 sec
    assert machine.can_request() is True

    # make the timestamp now with all else the same, should trigger the edge case
    # where limit is reached, we're past the reset window, and we recorded a request
    # with a time past the reset window (reset window past and we already made a
    # request, but the limit is still zero!)
    machine.timings.update_timestamp()
    assert machine.can_request() == (False, RequestMachineStates.EdgeCaseError)


def test_can_request_integration():
    """
    This test is an integration level test, ensuring
    all the timings are updated and that can_request
    is proper.
    """

    # test keys
    token_key = 'token'
    token_value = '0000000000'

    send_headers = {
        token_key: token_value
    }

    request_spec = RequestSpec(uri='mock://github/events/limits', send_headers=send_headers,
                               time_to_reset=timeutils.milliseconds() - 100000,
                               rate_limit_remaining=0)
    machine = mock_requests.create_mock_request_machine(request_spec)

    assert machine is not None
    assert machine.state == RequestMachineStates.Idle
    assert machine.request_spec.send_headers == send_headers
    assert machine.session.headers.get(token_key) == token_value

    # Initial get will pass, but response will have limit of 0
    resp = machine.get()
    assert resp is None
    assert machine.state == RequestMachineStates.EdgeCaseError
    assert machine.timings.rate_limit_remaining == '0'

    # second time around the resp will be None and state in waiting
    # since we'll manually set the reset timing to a future time.
    # Also we must reset both the machine state as is in an error state
    # from above, and also the time stamp to minus 1, since interval
    # by default is set to 1 (second). Else the edge case will
    # reappear as it does above.
    machine.timings.last_request_timestamp = timeutils.milliseconds() - 1000
    machine.timings.time_to_reset = str(timeutils.milliseconds() + 200000)
    machine.reset_state()
    resp = machine.get()
    assert resp is None
    assert machine.state == RequestMachineStates.WaitingForReset


def atest_mock_request_machine():
    """
    This test is large because it must test the machine and it's state
    over many requests.
    """

    # test keys
    token_key = 'token'
    token_value = '0000000000'

    send_headers = {
        token_key: token_value
    }

    request_spec = RequestSpec(uri='mock://github/events', send_headers=send_headers,
                               time_to_reset=str(timeutils.milliseconds() - 100000))
    ifnonmatch = request_spec.headers.ifnonmatch.lower()
    machine = mock_requests.create_mock_request_machine(request_spec)

    assert machine is not None
    assert machine.state == RequestMachineStates.Idle
    assert machine.request_spec.send_headers == send_headers
    assert machine.session.headers.get(token_key) == token_value

    # == From here state is waiting ==
    # get data, should also pass but this request doesn't pass
    # the timing, and will not do a get since it will be in a
    # waiting state
    resp = machine.get()
    assert resp is not None

    # reset the time to reset to max, force get to be None
    request_spec.time_to_reset = 9999999999
    machine = mock_requests.create_mock_request_machine(request_spec)
    resp = machine.get()

    # assert the session still has the same persisted headers
    assert machine.session.headers.get(token_key) == token_value
    # on first request, machine starts with no etag
    assert machine.session.headers.get('etag') is None

    # assert the response
    assert resp is None
    assert machine.state == RequestMachineStates.WaitingForReset

    # == From here state will be ready to get ==
    # reset spec and do a clean get
    request_spec = RequestSpec(uri='mock://github/events')
    machine = mock_requests.create_mock_request_machine(request_spec)
    resp = machine.get()
    assert resp is not None

    # check that etag from previous response is now
    # part of ifnonmatch header
    assert machine.session.headers.get(ifnonmatch) == RequestSpec.wrap(mock_requests.GLOBAL_MOCK_REQUEST_ETAG1)

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

    # now hit the mock backend that responds with a 304
    # reach into the machine and mutate the uri that
    # would have been set by the request spec
    machine.request_spec.uri = 'mock://github/events/withetag'
    resp = machine.get()
    assert resp is not None
    assert resp.status_code == 304
    assert machine.state == RequestMachineStates.WaitingForModifiedContent
    # assert that the timings still change even though a 304 was received
    assert machine.timings.interval == '20000'  # the mock response sets a new interval to 20

    # reset back to events for remainder of the test
    machine.request_spec.uri = 'mock://github/events'

    for x in range(0, 99):
        machine.get()

    assert machine.latency.data.get('count') == 101
    assert machine.latency_window.data.get('count') == 101

    # assert that percentiles were calculated
    # if the values below do not exist then
    # most likely timings are not being marked
    assert machine.latency.data.get('99percentile') is not None
    assert machine.latency.data.get('stddev') is not None
    assert machine.latency.data.get('mean') is not None

# on first call flag
# set limits based on resp

