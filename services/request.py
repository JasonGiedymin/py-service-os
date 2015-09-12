__author__ = 'jason'

from enum import Enum
from greplin import scales
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
        self.reset = reset
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
                 interval=60,
                 rate_limit=1,
                 rate_limit_remaining=1,
                 rate_limit_ttr=60,
                 headers=RequestHeaders()):
        self.uri = uri
        self.interval = interval
        self.rate_limit = rate_limit
        self.rate_limit_remaining = rate_limit_remaining
        self.rate_limit_ttr = rate_limit_ttr  # ttr = time till reset
        self.headers = headers


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
    def __init__(self, session, request_spec):
        self.uuid = uuid4()
        self.stats = scales.collection('/request-machine/%s' % self.uuid, scales.PmfStat('latency'))
        self.session = session
        self.request_spec = request_spec
        self.cache = {}  # general cache
        self.state = RequestMachineStates.Idle

    def get(self):
        self.state = RequestMachineStates.Processing

        with self.stats.latency.time():
            resp = self.session.get(self.request_spec.uri)
            return resp
