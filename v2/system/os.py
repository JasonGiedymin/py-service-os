# external
import gevent
from gevent.queue import Queue
from greplin import scales

# lib
from v2.system.services import BaseService, DirectoryService
from v2.system.states import BaseStates, EventLoopStates
from v2.system.strategies import RoundRobinIndexer

__author__ = 'jason'


class ServiceManager(BaseService):
    """
    ServiceManager is in charge of starting or stopping services.
    """
    family_latency = scales.HistogramAggregationStat('latency')

    def __init__(self, name, parent_logger=None):
        scales.init(self, '/service-manager')
        BaseService.__init__(self, name, parent_logger=parent_logger)
        self._directory = {}
        self.started_services = Queue()
        self._directory_service_proxy = DirectoryService(self._directory, parent_logger=self.log)

    def start(self):
        BaseService.start(self)
        self._directory_service_proxy.start()

        self.log.info("starting services...")
        for service_name, service in self._directory.iteritems():
            self.log.info("starting service %s" % service_name)
            self.started_services.put(service.start())

    def add_service(self, service, name):
        """
        Add service to service manager by name.
        :param service:
        :param name:
        :return:
        """
        self.log.debug("service %s added" % name)
        service.set_directory_service_proxy(self._directory_service_proxy)
        self._directory[name] = service

    def stop_service(self, name):
        """
        :param greenlet:
        :return:
        """
        self.log.debug("stopping services...")
        service = self._directory_service_proxy.get_service(name)
        gevent.kill(service)
        self._directory.pop(service)

    def stop_services(self):
        for pid_key, pid in self._directory.items():
            pid.stop()

    def get_directory_service_proxy(self):
        return self._directory_service_proxy

    def get_service_count(self):
        return self._directory_service_proxy.get_service_count()

    def get_services(self):
        return self._directory.items()


class Scheduler(BaseService):
    """
    The scheduler at this point is in charge of scheduling a service action
    with a local or group of service managers or a mix with remote service
    managers.
    """
    def event_loop_next(self):
        return EventLoopStates(self.event_loop_state.next())._name_

    def __init__(self, name, parent_logger=None):
        BaseService.__init__(self, name, parent_logger=parent_logger)
        self._service_manager = ServiceManager("service-manager", parent_logger=self.log)  # workers each handle one rest endpoint
        self.event_loop_state = RoundRobinIndexer(2)
        self.log.debug("Initialized.")

    def event_loop(self):
        while self._service_state:
            self.event_loop_next()
            gevent.sleep(.5)

    def get_service_manager(self):
        return self._service_manager

    def add_service(self, service):
        self._service_manager.add_service(service, service.name)

    def get_services(self):
        return self.get_service_manager().get_services()

    def get_services_count(self):
        return self._service_manager.get_service_count()

    def start(self):
        BaseService.start(self)
        self._service_manager.start()
        return self.greenlet

    def stop(self):
        self._service_manager.stop_services()
        self._service_manager.stop()
        BaseService.stop(self)


class CannedOS(BaseService):
    """
    OS -> Scheduler -> ServiceManager -> DirectoryService -> UserService

    There is an operating system defined as OS.

    The OS runs a scheduler service named Scheduler, which runs
    core services. An example core service is the ServiceManager.

    ServiceManager serves to manage services, but interaction with
    it is through the scheduler.

    A custom service which is started by the ServiceManager
    is a service catalogue named DirectoryService. All services
    are registered with it and other services can find each other
    with the directory.

    Starting and stopping of services are done by the ServiceManager.

    The end user when adding user services uses the OS level method schedule().
    Remember that all services are stored with the directory service.
    User services however are named as a child of the OS, rather than
    a named child of the fully qualified hierarchy. The only place where
    a full name hierarchy is retained is with the core services (scheduler,
    service manager, and directory service).

    """
    def __init__(self, name):
        BaseService.__init__(self, name)
        self.scheduler = Scheduler("scheduler", parent_logger=self.log)

    def bootup(self):
        self.log.debug("booting up...")
        self.scheduler.start()

    def shutdown(self):
        self.log.debug("shutting down...")
        self.scheduler.stop()
        self.stop()

    def schedule(self, service_class, name):
        """
        Take a service and let the instaniation begin here.
        :param service_class:
        :param name:
        :return:
        """
        service = service_class(name, parent_logger=self.log)
        self.scheduler.add_service(service)

    def event_loop(self):
        """
        The event loop.
        """
        while True:
            self.log.debug("OS says hi")
            gevent.sleep(1)
