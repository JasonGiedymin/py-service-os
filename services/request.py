from enum import Enum
from time import time
from uuid import uuid4
import logging

from greplin import scales
from greplin.scales import meter
import requests

from system.services import BaseService, BaseStates
from utils import timeutils

__author__ = 'jason'


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
                 interval=1000,  # interval is in milliseconds
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
        self.last_request_timestamp = self.get_now()

    @staticmethod
    def get_now():
        return timeutils.milliseconds()

    def update_timestamp(self):
        self.last_request_timestamp = self.get_now()

    def update(self, resp):
        """
        Updates the timing object based on the response received from the
        server.
        """
        # the lag in updating the timestamp is a nice security blanket
        # to prevent to quick of a request
        self.update_timestamp()
        self.interval = str(resp.headers.get(self.spec.headers.interval))
        self.rate_limit = str(resp.headers.get(self.spec.headers.rate_limit))
        self.rate_limit_remaining = str(resp.headers.get(self.spec.headers.rate_limit_remaining))
        self.time_to_reset = str(resp.headers.get(self.spec.headers.time_to_reset))
        etag = self.spec.headers.etag.lower()
        self.etag = resp.headers.get(etag)


class RequestService(BaseService):
    def __init__(self, name, request_spec, session=requests.Session()):
        BaseService.__init__(self, name)
        self.request_spec = request_spec
        self.machine = RequestMachine(session, request_spec)

    def event_loop(self):
        self.log.debug("tick")


class RequestMachineStates(Enum):
    Idle = 0
    WaitingOnResponse = 1
    Error = 2
    Processing = 3
    Stopped = 4
    WaitingForReset = 5
    WaitingForModifiedContent = 6  # if 304 Not Modified content via etag
    WaitingForIntervalToPass = 7
    EdgeCaseError = 8  # edge case that causes error


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

    console = logging.StreamHandler()
    format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
    console.setFormatter(logging.Formatter(format_str))

    def __init__(self, session, request_spec):
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(self.console)
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
        time_stamp = self.timings.last_request_timestamp
        ttr = float(self.timings.time_to_reset)
        now = timeutils.milliseconds()

        # last time called was before or at the reset and
        # time now is at or beyond the reset allow
        if time_stamp <= ttr and now >= ttr:
            print "ts less than ttr and now greater than ttr"
            return True
        else:
            return False

    def limit_reached(self):
        return int(self.timings.rate_limit_remaining) <= 0

    def past_interval(self):
        now = timeutils.milliseconds()
        last = self.timings.last_request_timestamp
        estimated_interval_ts = last + float(self.timings.interval)
        result = now > estimated_interval_ts

        if not result:
            self.log.debug("now (%d) not yet past the interval (%d)" % (now, estimated_interval_ts))

        return result

    def past_reset_window(self):
        now = timeutils.milliseconds()
        reset_window = float(self.timings.time_to_reset)
        result = now >= reset_window

        if not result:
            self.log.debug("request not yet past reset window")

        return result

    def request_made_since_reset_window(self):
        timestamp = float(self.timings.last_request_timestamp)
        reset_window = float(self.timings.time_to_reset)
        result = timestamp >= reset_window

        if result:
            self.log.warn("request was made since reset window")

        return result

    def edge_case(self):
        result = self.limit_reached \
               and self.past_reset_window() \
               and self.request_made_since_reset_window()

        if result:
            self.log.error("RequestMachine edge case detected")

        return result

    def can_request(self):
        if self.edge_case():
            return False, RequestMachineStates.EdgeCaseError

        if self.past_interval():
            # if the limit has been reached
            if not self.limit_reached():
                return True
            else:  # limit reached
                if self.past_reset_window():  # limit should be reset
                    return True
                return False, RequestMachineStates.WaitingForReset

        return False, RequestMachineStates.WaitingForIntervalToPass

    def _update(self, resp):
        self.timings.update(resp)
        self._seed_temporal_data()

    def _idle_state(self):
        self.state = RequestMachineStates.Idle

    def _error_state(self):
        self.state = RequestMachineStates.Error

    def _processing_state(self):
        self.state = RequestMachineStates.Processing

    def reset_state(self):
        self._idle_state()

    def has_error_state(self):
        return self.state == RequestMachineStates.Error \
               or self.state == RequestMachineStates.EdgeCaseError

    def get(self):
        if self.has_error_state():
            print "Cannot proceed, machine is in ERROR state. Please see the logs."
            return None

        can_request, proposed_error_state = self.can_request()

        if can_request:
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
            self.state = proposed_error_state
            return None

