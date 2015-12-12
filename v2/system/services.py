from uuid import uuid4
import gevent
from gevent.queue import Queue
from greplin import scales
from greplin.scales import meter

from v2.system.states import BaseStates
from v2.system.exceptions import IdleActionException, ServiceNotIdleException
from v2.utils.loggers import Logger


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
        Override this
        """
        # while True:
        #     with self.latency.time():
        #         self.latency_window.mark()
        #         # do some work here
        #         # sleep or idle
        while self.should_loop():
            gevent.idle()

    def should_loop(self):
        # return not self.ready() or not self.has_stopped()
        # chose to signal on if the service has started rather than started or idle
        # which would be a confusing state which a loop would be allowed execution.
        # In an effort to narrow down to one state I choose `started`.
        return self.has_started()

    def __init__(self, name="base-service", directory_proxy=None, parent_logger=None, enable_service_recovery=False):
        """
        uuid - a uuid4 value for the service
        alias - a colloquial alias
        unique_name - a name which includes an easier to remember alias with the uuid

        :param name:
        :param directory_proxy:
        :param parent_logger:
        :return:
        """
        self.uuid = uuid4()  # unique uuid
        self.alias = name  # name, may collide
        self.unique_name = '%s/%s' % (self.alias, self.uuid)  # a unique name for this service, will always be unique
        scales.init(self, self.unique_name)

        if parent_logger is None:  # no parent, use fq name
            self.lineage = "%s" % self.unique_name
        else:
            parent_name = parent_logger._context["name"]
            self.lineage = "%s/%s" % (parent_name, self.unique_name)

        self.log = Logger.get_logger(self.lineage)
        self.greenlet = None
        self._service_state = None
        self.set_state(BaseStates.Idle)

        # directory service proxy
        self._directory_proxy = directory_proxy

        # service recovery option
        self.enable_service_recovery = enable_service_recovery

        self.log.debug("Initialized.")

    def register_child_stat(self, name):
        scales.initChild(self, name)

    def register(self):
        """
        Once a service has been actively managed, it is populated
        by the service manager with addtional information or services.
        This method registers that data.
        Typically you will find a database and queue proxy to be set
        here.
        :return:
        """
        pass

    def start(self):
        self.log.info("Starting...")

        if self.get_state() is not BaseStates.Idle:  # or not self.enable_service_recovery:
            self.log.error("could not start service as it is not in an idle state, current state: [%s]" % self.get_state())
            raise ServiceNotIdleException()

        self.greenlet = gevent.spawn(self.event_loop)
        self.set_state(BaseStates.Started)
        return self.greenlet

    def stop(self):
        self.log.info("Stopping...")

        if self.greenlet is not None:
            gevent.kill(self.greenlet)
        else:
            self.log.warn("service [%s] was found already stopped." % self.lineage)

        self.set_state(BaseStates.Stopped)
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

    def has_started(self):
        return self.get_state() is BaseStates.Started

    def has_stopped(self):
        return self.get_state() is BaseStates.Stopped

    def has_state(self):
        return self.get_state() is not None

    def is_zombie(self):
        """
        If there is no state such as Idle, Start, or Stop then this service
        is a zombie.
        :return:
        """
        return not self.has_state() or not self.greenlet.started

    def idle(self):
        """
        Resets a service which you expect to restart.
        Prior to started a service it must be set to idle.
        :return:
        """
        if self.get_state() is BaseStates.Stopped or self.is_zombie():
            self.set_state(BaseStates.Idle)
        else:
            raise IdleActionException()

    def get_state(self):
        return self._service_state

    def set_state(self, state):
        """
        Should be used only by base class and inheritors
        """
        self.log.debug("Service state is being set to: [%s]" % state)
        self._service_state = state

    def set_directory_service_proxy(self, directory_proxy):
        self._directory_proxy = directory_proxy

    def get_directory_service_proxy(self):
        return self._directory_proxy


class ExecutionService(BaseService):
    """
    An execution service is really a symantic object that holds references to
    services. Itself should not run an event loop.
    """
    def should_loop(self):
        return False

    def event_loop(self):
        gevent.idle()


class QueuedService(BaseService):
    """
    This is a service which one expects output to be tracked. The mechanism
    is via the use of an output_queue of type gevent.Queue. Use this as an
    output buffer, allowing a worker to do what it does best which is to
    work.
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
    dictionary. At least to control mishaps. This is
    essentially a service catalogue.
    """
    def __init__(self, service_manager_directory, parent_logger=None):
        BaseService.__init__(self, "directory-service", parent_logger=parent_logger)
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

    def event_loop(self):
        while True:
            # print "%s - working" % self.name
            gevent.sleep(.5)
