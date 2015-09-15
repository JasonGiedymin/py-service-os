__author__ = 'jason'

from enum import Enum
from greplin import scales
from greplin.scales import meter
from uuid import uuid4

from system.services import BaseService, BaseStates


class RequestHeaders:
    def __init__(self,
                 interval='X-Poll-Interval',
                 limit='X-RateLimit-Limit',
                 limit_remaiming='X-RateLimit-Remaining',
                 reset='X-RateLimit-Reset'):
        self.interval = interval
        self.rate_limit = limit
        self.rate_limit_remaining = limit_remaiming
        self.time_to_reset = reset
        self.etag = 'ETag'
        self.cache_control = 'Cache-Control'
        self.last_modified = 'Last-Modified'


class RequestSpec:
    """
    Request spec which will be used to drive a request service.
    Any fields corresponding to time do so with seconds as the
    unit of time.
    """
    def __init__(self,
                 uri=None,
                 interval=1,
                 rate_limit=1,
                 rate_limit_remaining=1,
                 time_to_reset=60,
                 headers=RequestHeaders()):
        self.uri = uri
        self.interval = interval
        self.rate_limit = rate_limit
        self.rate_limit_remaining = rate_limit_remaining
        self.time_to_reset = time_to_reset  # ttr = time till reset
        self.headers = headers


class RequestTimings:
    """
    Object to hold current request timings.
    """
    def __init__(self, spec):
        self.spec = spec
        self.interval = str(spec.interval)
        self.rate_limit = str(spec.rate_limit)
        self.rate_limit_remaining = str(spec.rate_limit_remaining)
        self.time_to_reset = str(spec.time_to_reset)  # ttr = time till reset

    def update(self, resp):
        self.interval = str(resp.headers.get(self.spec.headers.interval))
        self.rate_limit = str(resp.headers.get(self.spec.headers.rate_limit))
        self.rate_limit_remaining = str(resp.headers.get(self.spec.headers.rate_limit_remaining))
        self.time_to_reset = str(resp.headers.get(self.spec.headers.time_to_reset))


class RequestService(BaseService):
    def __init__(self, request_spec):
        self.request_spec = request_spec

    def event_loop(self):
        pass


class RequestMachineStates(Enum):
    Idle = 0
    WaitingOnSend = 1
    Error = 2
    Processing = 3
    Stopped = 4


class RequestMachine:
    """
    Don't use IDLE as the primary state identifier when
    trying to find out if the first request has been sent.
    Use stats instead. One may put the machine in idle
    after stopping, and it would still use the cached
    limits.
    """

    # state averages from 75, 95, 98, 99, 999,
    # min, max, median, mean, and stddev
    latency = scales.PmfStat('latency')

    # timing for 1/5/15 minute averages
    latency_window = meter.MeterStat('latency_window')

    def __init__(self, session, request_spec):
        # BaseService.__init__(self)
        self.uuid = uuid4()  # unit identifier
        scales.init(self, '/request-machine/%s' % self.uuid)
        # self.register_child_stat('/request-machine/%s' % self.uuid)
        self.session = session  # request http session
        self.request_spec = request_spec  # request spec with spec of call
        self.timings = RequestTimings(request_spec)
        self.state = RequestMachineStates.Idle  # current state

    def get(self):
        self.state = RequestMachineStates.Processing

        with self.latency.time():
            self.latency_window.mark()
            resp = self.session.get(self.request_spec.uri)
            self.timings.update(resp)
            self.state = RequestMachineStates.Idle
            return resp

