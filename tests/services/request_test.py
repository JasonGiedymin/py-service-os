__author__ = 'jason'

from services.request import RequestSpec, RequestMachineStates
from tests.system import mock_requests


def test_mock_request_machine():
    # init
    request_spec = RequestSpec(uri='mock://github/events')
    machine = mock_requests.create_mock_request_machine(request_spec)
    assert machine is not None
    assert machine.state == RequestMachineStates.Idle

    # get data
    resp = machine.get()
    assert resp is not None
    assert machine.stats.latency.data.get('count') == 1


# on first call flag
# set limits based on resp

