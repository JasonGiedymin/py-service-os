from uuid import uuid4
import logging
import gevent
from gevent.queue import Queue
from greplin import scales
from greplin.scales import meter

from states import BaseStates
from exceptions import IdleActionException
from data.loggers import Logger

__author__ = 'jason'


class BaseService:
    """
    A base service. Note this is a class which
    composites a greenlet. This is in contrast
    with the Actor class which subclasses greenlet
    for performance and being lightweight. This
    class is still aimed for performance but has
    many management routines and actions which are
    necessary.
    """

    # state averages from 75, 95, 98, 99, 999,
    # min, max, median, mean, and stddev
    latency = scales.PmfStat('latency')

    # timing for 1/5/15 minute averages
    latency_window = meter.MeterStat('latency_window')

    # console = logging.StreamHandler()
    # format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
    # console.setFormatter(logging.Formatter(format_str))

    def event_loop(self):
        """
        Override
        """
        # while True:
        #     with self.latency.time():
        #         self.latency_window.mark()
        #         # do some work here
        #         # sleep or keep going
        pass

    def __init__(self, name="base-service", directory_proxy=None):
        self.uuid = uuid4()
        self.unique_name = '/%s/%s' % (name, self.uuid)
        scales.init(self, self.unique_name)

        # self.log = logging.getLogger(self.unique_name)
        # self.log.setLevel(logging.DEBUG)
        # self.log.addHandler(self.console)
        self.log = Logger.get_logger(self.unique_name)

        print "%s - Init" % name
        self.name = name
        self.greenlet = None
        self._service_state = BaseStates.Idle

        # directory service proxy
        self._directory_proxy = directory_proxy

    def register_child_stat(self, name):
        scales.initChild(self, name)

    def start(self):
        # print "%s - Starting..." % self.name
        self.greenlet = gevent.spawn(self.event_loop)
        self._service_state = BaseStates.Started
        return self.greenlet

    def stop(self):
        # print "%s - Stopping..." % self.name
        gevent.kill(self.greenlet)
        self._service_state = BaseStates.Stopped
        return self.greenlet

    def get_greenlet(self):
        return self.greenlet

    def ready(self):
        """
        Only return true when state is Idle which means
        it is ready to accept specs to start. Start
        should assume the service is already acting on
        a user's request for 'work'. This is an boolean
        alias to check if in Idle state.
        :return:
        """
        if self.get_state() is BaseStates.Idle:
            return True

        return False

    def idle(self):
        if self.get_state() is BaseStates.Stopped:
            self._service_state = BaseStates.Idle
        else:
            raise IdleActionException()

    def get_state(self):
        return self._service_state

    def set_state(self, state):
        """
        Should be used only by base class and inheritors
        """
        self._service_state = state

    def set_directory_service_proxy(self, directory_proxy):
        self._directory_proxy = directory_proxy

    def get_directory_service_proxy(self):
        return self._directory_proxy


class OutputService(BaseService):
    """
    This is a service which one expects output
    to be tracked. The mechanism is via the use
    of an output_queue of type gevent.Queue.
    As opposed to a scheduled
    service which is almost a fire and forget.
    Note that a fire and forget is great where
    it can still log output to an external
    system for deferred parsing.
    """
    def __init__(self, name, size=None, items=None):
        BaseService.__init__(self, name)
        self._queue = Queue(size, items)

    def put(self, item, block=True, timeout=None):
        return self._queue.put(item, block, timeout)

    def get(self, block=True, timeout=None):
        """
        Gets from the backing Queue.
        If calling get on empty Queue, it will block
        until Queue actually has contents to return.
        If that is undesired set block=False to prevent
        greenlet blocking.
        :param block:
        :param timeout:
        :return:
        """
        return self._queue.get(block, timeout)

    def size(self):
        return self.queue_ref().qsize()

    def queue_ref(self):
        """
        Direct access if necessary. Warning this will allow
        direct access for modification. Tend not to use it.
        :return:
        """
        return self._queue


class DirectoryService(BaseService):
    """
    Proxy for directory dictionary as opposed to the full
    dictionary. At least to control mishaps.
    """
    def __init__(self, service_manager_directory):
        BaseService.__init__(self, "directory-service")
        self._service_manager_directory = service_manager_directory

    def event_loop(self):
        pass

    def get_service_count(self):
        return len(self._service_manager_directory)

    def get_service(self, name):
        return self._service_manager_directory.get(name)

    def get_outputservice(self):
        return self._service_manager_directory.get("output-service")


class TestWorker(BaseService):
    def __init__(self, name):
        BaseService.__init__(self, name)
        # self.name = "test-worker-1"

    def event_loop(self):
        while True:
            # print "%s - working" % self.name
            gevent.sleep(.5)


class RequestSpec:
    def __init__(self):
        pass


class RequestWorker:
    # do work
    # take requestspec
    def __init__(self, spec):
        self.spec = spec
        self.greenlet = None
        self.on = False

    def work(self):
        while self.on:
            # print("Working on http request")
            gevent.sleep(1)

    def start(self):
        print "starting..."
        self.on = True
        self.greenlet = gevent.spawn(self.work)
        return self.greenlet

    def stop(self):
        self.on = False
        # print "<- Stopped!"
        gevent.kill(self.greenlet)

# w = RequestWorker(RequestSpec())
# gevent.spawn_later(10, w.stop)
# gevent.joinall([w.start()])
