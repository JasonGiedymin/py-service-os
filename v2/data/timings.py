from v2.utils import timeutils
from v2.utils.loggers import Logger
from v2.data.states import ResourceStates

from uuid import uuid4
from enum import Enum


__author__ = 'jason'


class ResourceHeaders:
    """
    Resource Headers is the mapping for request headers which the resource
    will use to parse the response with.
    """
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


class Resource:
    """
    Basic structure representing a resource.
    """
    def __init__(self,
                 uri,
                 timings,
                 headers=ResourceHeaders(),
                 send_headers={},
                 owner=""
                 ):
        """
        When New resources are created a unique name is generated and
        should be saved along with the resource.
        """
        self.uri = uri
        self.id = uuid4()  # unique id representing the resource
        self.unique_name = '/%s/%s' % (self.id, self.uri)
        self.timings = timings
        self.headers = headers
        self.send_headers = send_headers

        # a string representing the guid of an
        # owner which is working on the resource
        self.owner = owner  # I would expect to see the unique name of an application here (111223-analyzer)

        # this represents the queue that the resource is now in
        self.queue_topic = "NONE"

        self.state = ResourceStates.Idle

    def has_owner(self):
        return len(self.owner) > 0

    def is_new(self):
        return self.timings.last_request_timestamp is None

    def has_error(self):
        return self.state == ResourceStates.Error

    def __repr__(self):
        return '{"resource":{"id":"%s","uri":"%s"}}' % (self.id, self.uri)


class ResourceTimings:
    """
    Structure to hold current request timings.
    Though external APIs may deal with second resolution, internally
    we can deal with milliseconds. This is done through two
    important timing vars:
        - interval: in milliseconds
        - time_to_reset: in milliseconds
    """
    def __init__(self,
                 interval=1000,  # interval is in milliseconds
                 rate_limit=1,
                 rate_limit_remaining=1,
                 time_to_reset=60,
                 etag=None
                 ):
        self.interval = interval
        self.rate_limit = rate_limit
        self.rate_limit_remaining = rate_limit_remaining
        self.time_to_reset = time_to_reset  # this is time to reset in milliseconds
        self.etag = etag
        self.interval_timestamp = None  # this is the timestamp which the next interval checkpoint would be
        self.last_request_timestamp = None

    @staticmethod
    def get_now():
        return timeutils.milliseconds()

    def update_timestamp(self):
        self.last_request_timestamp = self.get_now()

    def update_interval_timestamp(self, use_now=False):
        """
        This will update the interval timestamp. Helpful in needing
        to know when the interval has cycled.
        :return:
        """
        if use_now:
            self.interval_timestamp = self.get_now() + self.interval
        else:
            self.interval_timestamp = self.last_request_timestamp + self.interval

    def has_limit_been_reached(self):
        return self.rate_limit_remaining == 0

    def has_reset_window_past(self):
        # compares now and if it is greater than the recorded reset window
        now = timeutils.milliseconds()
        return now > self.time_to_reset

    def requested_since_reset(self):
        # compares if a request was made since the reset value. A request
        # should never be recorded with a time after a reset.
        # if a request was indeed made but the reset window is still
        # in the past, this could signal an error with the response
        return self.last_request_timestamp > self.time_to_reset

    def has_interval_passed(self, now=None):
        """
        This method may accept a value for now, otherwise it will
        generate now (in milliseconds) upon calling execution.
        :param now:
        :return:
        """
        if now is None:  # else use the provided 'now'
            now = self.get_now()

        return now > self.interval_timestamp

    def update(self, response, header_keys):
        def get_value(key, key_type=str):
            return self.get_header_value(response.headers,
                                         key,
                                         key_type)

        self.interval = get_value(header_keys.interval, int)  # milliseconds
        self.rate_limit = get_value(header_keys.rate_limit, int)
        self.rate_limit_remaining = get_value(header_keys.rate_limit_remaining, int)
        self.time_to_reset = get_value(header_keys.time_to_reset, int) * 1000  # seconds need to convert to milliseconds
        self.etag = get_value(header_keys.etag)
        self.update_timestamp()

    @staticmethod
    def get_header_value(headers, header_key, key_type=str):
        if type(key_type) is str:
            return headers.get(header_key)

        return key_type(headers.get(header_key))


