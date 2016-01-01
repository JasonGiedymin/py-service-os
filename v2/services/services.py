from uuid import uuid4
import time
import gevent
from gevent.queue import Queue
from greplin import scales
from greplin.scales import meter

from v2.system.states import BaseStates
from v2.services.error_handler import ErrorHandlerMixin
from v2.system.exceptions import IdleActionException, ServiceNotIdleException
from v2.utils.loggers import Logger


__author__ = 'jason'


class BaseService(ErrorHandlerMixin):
    """
    A base service. Note this is a class which composites a greenlet. This is in
    contrast with the Actor class which subclasses greenlet and may be more
    performant and lightweight. This class is still aimed for performance but
    has many management routines and actions.

    This base class has many of the same attributes as the underlying gevent
    greenlet but note they are not the same. Effort was made to make semantic
    usage easier. Do not assume anything similar with gevent.
    """

    # state averages from 75, 95, 98, 99, 999,
    # min, max, median, mean, and stddev
    latency = scales.PmfStat('latency')

    # timing for 1/5/15 minute averages
    latency_window = meter.MeterStat('latency_window')

    # console = logging.StreamHandler()
    # format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
    # console.setFormatter(logging.Formatter(format_str))

    def __init__(self,
                 name="base-service",
                 directory_proxy=None,
                 parent_logger=None,
                 enable_service_recovery=False):
        """
        uuid - a uuid4 value for the service
        alias - a colloquial alias
        unique_name - a name which includes an easier to remember alias with the uuid

        :param name:
        :param directory_proxy:
        :param parent_logger:
        :return:
        """
        ErrorHandlerMixin.__init__(self)

        # time indexes
        self.time_starting_index = None  # time index when service was 'starting'
        self.time_started_index = None  # time index when service was started

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
        self.directory_proxy = directory_proxy

        # service recovery option
        self.enable_service_recovery = enable_service_recovery

        self.log.debug("Initialized.")

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

    def did_service_timeout(self):
        """
        A timeout occurs when a service remains in the starting phase.
        :return:
        """
        timeout = self.get_directory_service_proxy().get_service_meta(self.alias).start_timeout

        if timeout > 0 and self.is_starting():
            delay = self.get_directory_service_proxy().get_service_meta(self.alias).delay
            timeout = self.get_directory_service_proxy().get_service_meta(self.alias).start_timeout

            # calculate by adding the delay that will be introduced
            # with the timeout value, and this time index will be the maximum time
            # which with to wait for the service to start
            expected_timeout = delay + timeout

            # now determine if the time that has passed has met or exceeded the
            # calculated timeout index from above
            return self.start_time_delta() >= expected_timeout

        return False

    def start_time_delta(self):
        """
        Returns the time difference between now and when the service entered into the
        `Starting` state. This is how long since the service first indexed as being
        in been in the `Starting` position. Note that this will always calculate,
        and should be used as a utility method.
        :return:
        """
        now = time.time()
        return now - self.time_starting_index

    def start_event_loop(self):
        self.log.debug("service starting event loop...")
        self.set_state(BaseStates.Started)
        self.time_started_index = time.time()
        self.event_loop()

    def start(self, delay=0):
        if self.get_state() is not BaseStates.Idle:  # or not self.enable_service_recovery:
            self.log.error("could not start service as it is not in an idle state, current state: [%s]" %
                           self.get_state(), state=self.get_state())
            raise ServiceNotIdleException()

        if delay > 0:
            self.log.debug("service starting with delay...", delay=delay)
            self.time_starting_index = time.time()
            self.greenlet = gevent.spawn_later(delay, self.start_event_loop)
            self.set_state(BaseStates.Starting)
        else:
            self.log.debug("service starting...")
            self.set_state(BaseStates.Starting)  # TODO: time how long services take to actually start
            self.greenlet = gevent.spawn(self.start_event_loop)

        #
        # --- NO CODE BEYOND THE IF/ELSE BLOCK ABOVE ---
        #
        # this method works asynchronously and thus code here will execute immediately

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

    def is_starting(self):
        return self.get_state() is BaseStates.Starting

    def has_state(self):
        return self.get_state() is not None

    def is_zombie(self):
        """
        If there is no state such as Idle, Start, or Stop then this service
        is a zombie.
        :return:
        """
        return not self.has_state() or not self.greenlet.started

    def is_truly_dead(self):
        """
        Not a zombie. Stopped is not dead. Zombie is not dead (It's alive stupid!).
        This method checks if the greenlet was not successful and has logged an
        exception.

        Note: below I don't check for service.idle() because that is a sign that
        a service is alive and about to be started. Instead I focus on the greenlet
        which if was created will still have values such as exception and successful
        registered.
        :return:
        """
        return self.greenlet is not None \
            and not self.greenlet.successful() \
            and self.greenlet.exception is not None

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
        self.directory_proxy = directory_proxy

    def get_directory_service_proxy(self):
        return self.directory_proxy


class ExecutorService(BaseService):
    """
    An execution service is really a symantic object that holds references to
    services. Itself should not run an event loop. It will register as
    `BaseStates.Idle` when created, however it will remain in that state.
    These are services which for now are code bundles, that in the future
    could be an event loop processor.
    """
    def should_loop(self):
        return False

    def event_loop(self):
        """
        Effectively a one loop pass.
        :return:
        """
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

    def get_service(self, alias):
        return self._service_manager_directory.get(alias).service

    def get_service_meta(self, alias):
        return self._service_manager_directory.get(alias).service_meta

    def get_service_entry(self, alias):
        return self._service_manager_directory.get(alias)

    def get_outputservice(self):
        return self._service_manager_directory.get("output-service")


class TestWorker(BaseService):
    def __init__(self, name):
        BaseService.__init__(self, name)

    def event_loop(self):
        while True:
            # print "%s - working" % self.name
            gevent.sleep(.5)
