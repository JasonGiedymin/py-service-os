__author__ = 'jason'


# External
from enum import Enum
import gevent
from gevent import Greenlet

# Lib
from limits import Limit


class States(Enum):
    Idle = 0
    Running = 1
    Failed = 2


class GHRequestEngine(Greenlet):
    """
    Basic GitHub request engine.
    """

    def __init__(self, session):
        # register as greenlet
        Greenlet.__init__(self)

        self.session = session

        # Resp cache to store data
        self.cache = {}

        # Limits used in operation
        self.limits = {}

        # gevent threads
        threads = []

        # engine state
        self._set_idle()

    def _run(self):
        print('running...')

    def get_state(self):
        return self.state

    def _set_idle(self):
        self.state = States.Idle

    def _set_running(self):
        self.state = States.Running

    def get(self, url, data_type):
        self._set_running()

        if data_type is None:
            raise "You must specify data_type in function call."

        if url is None:
            raise "You must specify a url."

        if data_type not in self.limits:
            resp = self.session.get(url)
            new_limit = Limit(resp)
            # this is post processing time, gives us a little bit of room to play but could be slow later
            new_limit.set_last_op_time()
            self.limits[data_type] = new_limit
        else:  # we have seen the request and a limit exists
            curr_limit = self.limits[data_type]
            interval = curr_limit.xpoll_interval
            gevent.sleep(int(interval)) if curr_limit and interval is not None else None
            resp = self.session.get(url)
            self.limits[data_type] = Limit(resp)

        self._set_idle()

        return resp

    def get_events(self, url="https://api.github.com/events", data_type="events"):
        """
        Quick method for just events.
        :param url:
        :param data_type:
        :return:
        """
        return self.get(url, data_type)

