__author__ = 'jason'

from enum import Enum
from time import time
from uuid import uuid4

from greplin import scales
from greplin.scales import meter

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
        self.ifnonmatch = 'If-None-Match'


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
                 etag=None,
                 headers=RequestHeaders(),
                 send_headers={}):
        self.uri = uri
        self.interval = interval
        self.rate_limit = rate_limit
        self.rate_limit_remaining = rate_limit_remaining
        self.time_to_reset = time_to_reset  # ttr = time till reset
        self.etag = etag
        self.headers = headers
        self.send_headers = send_headers

    @staticmethod
    def wrap(value):
        return '"' + value + '"'


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
        self.etag = spec.etag
        self.last_request_timestamp = time()  # needed to enforce poll interval

    def update(self, resp):
        """
        Updates the timing object based on the response received from the
        server.
        """
        self.interval = str(resp.headers.get(self.spec.headers.interval))
        self.rate_limit = str(resp.headers.get(self.spec.headers.rate_limit))
        self.rate_limit_remaining = str(resp.headers.get(self.spec.headers.rate_limit_remaining))
        self.time_to_reset = str(resp.headers.get(self.spec.headers.time_to_reset))
        etag = self.spec.headers.etag.lower()
        self.etag = resp.headers.get(etag)


class RequestService(BaseService):
    def __init__(self, request_spec):
        self.request_spec = request_spec

    def event_loop(self):
        pass


class RequestMachineStates(Enum):
    Idle = 0
    WaitingOnResponse = 1
    Error = 2
    Processing = 3
    Stopped = 4
    WaitingForReset = 5
    WaitingForModifiedContent = 6  # if 304 Not Modified content via etag


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
        self._seed_session()

    def _seed_temporal_data(self):
        # add temporal based headers (time limits, etag, etc...)
        if self.timings.etag is not None:
            self.session.headers.update({
                self.request_spec.headers.ifnonmatch: RequestSpec.wrap(self.timings.etag)
            })

    def _seed_session(self):
        # add all headers (token, auth, etc...)
        self.session.headers.update(self.request_spec.send_headers)

        self._seed_temporal_data()

    def limit_has_reset(self):
        """
        Call this if the remaining limit is 0.
        :return:
        """
        return time() > float(self.timings.time_to_reset)

    def _limit_reached(self):
        return self.timings.rate_limit_remaining <= 0

    def can_request(self):
        # if the limit has been reached
        if self._limit_reached:
            # but if the limit reset window is passed
            if self.limit_has_reset:
                # a request can be made
                return True

            # else the machine must wait
            return False

        # otherwise a request can be made
        return True

    def _update(self, resp):
        self.timings.update(resp)
        self._seed_temporal_data()

    def _idle_state(self):
        self.state = RequestMachineStates.Idle

    def _error_state(self):
        self.state = RequestMachineStates.Error

    def _processing_state(self):
        self.state = RequestMachineStates.Processing

    def get(self):
        if self.state == RequestMachineStates.Error:
            print "Cannot proceed, machine is in ERROR state. Please see the logs."
            return None

        if self.limit_has_reset():
            self._processing_state()

            with self.latency.time():
                self.latency_window.mark()
                resp = self.session.get(self.request_spec.uri)

                if resp.status_code == 304:
                    self.state = RequestMachineStates.WaitingForModifiedContent
                    # even with 304s, the server will still attempt
                    # to send limits back.
                    self._update(resp)
                    return resp
                elif resp.status_code == 200:
                    self._update(resp)
                    self._idle_state()
                    return resp
                else:
                    # TODO: log here
                    print "Request failed!"
                    print resp.status_code
                    print resp.content
                    self._error_state()

                    # even with 304s, the server will still attempt
                    # to send limits back.
                    self._update(resp)

                    self._idle_state()
                    return resp
        else:
            self.state = RequestMachineStates.WaitingForReset

