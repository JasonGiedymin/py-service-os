__author__ = 'jason'

import time


class LimitSpec:
    def __init__(self):
        pass


class Limit:
    """
    Limit object corresponding to a GitHub Api request response.
    Note: do not do inspection here, this a light container.
    """

    def __init__(self, response=None):
        if response is not None:
            # Note, that all these are case-sensitive and directly as they are from requests lib
            self.status_code = response.status_code
            self.etag = self._get_header_value(response, 'ETag')
            self.xpoll_interval = self._get_header_value(response, 'X-Poll-Interval')
            self.xrate_limit = self._get_header_value(response, 'X-RateLimit-Limit')
            self.xrate_limit_remaining = self._get_header_value(response, 'X-RateLimit-Remaining')
            self.next_reset = self._get_header_value(response, 'X-RateLimit-Reset')
            self.cache_control = self._get_header_value(response, 'Cache-Control')
            self.last_modified = self._get_header_value(response, 'Last-Modified')
        else:
            self.status = self.etag = self.xpoll_interval = self.xrate_limit = self.xrate_limit_remaining = None
            self.next_reset = None

        self.last_op_time = None

    def set_last_op_time(self):
        self.last_op_time = time.time()
        return self.last_op_time

    @staticmethod
    def _get_header_value(response, key):
        if key in response.headers:
            return response.headers[key]
        else:
            return None
