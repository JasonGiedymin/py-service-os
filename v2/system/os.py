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
        # self.started_services = []
        self._directory_service_proxy = DirectoryService(self._directory, parent_logger=self.log)
        self.set_directory_service_proxy(self._directory_service_proxy)  # since BaseService declares an interface

    def _start_services(self):
        """
        Starts all designated services from the internal directory.
        A service once stopped is removed from this directory and that
        prevents it from starting back up again.
        :return:
        """
        # started_services = []  # nice to know how many were started in this event loop
        started_services = 0

        def startable(): return service.ready() and not service.has_started()

        def recoverable(): return service.is_zombie() and service.enable_service_recovery

        def start_service(incoming_service):
                pid = incoming_service.start()
                if pid is not None:
                    return 1
                else:
                    return 0

        for service_name, service in self._directory.iteritems():
            if startable():
                self.log.info("starting service %s" % service_name)
                started_services += start_service(service)
            elif recoverable():
                # if a service is able to be recovered we must put it in the idle state
                service.idle()
                self.log.info("recovering and restarting possible zombied service: [%s]" % service_name)
                started_services += start_service(service)

        if started_services > 0:
            self.log.debug("started [%d] services in one event loop" % started_services)

        return started_services

    def start(self):
        BaseService.start(self)
        self._directory_service_proxy.start()

        self.log.info("starting services...")
        self._start_services()

        return self.greenlet

    def add_service(self, service, name):
        """
        Add service to service manager by name.
        :param service:
        :param name:
        :return:
        """
        self.log.debug("service %s added" % name)
        service.set_directory_service_proxy(self._directory_service_proxy)
        service.register()  # trigger and registration of data

        if name in self._directory:
            self.log.warn("service [%s] already exists" % name)
            return False

        self._directory[name] = service
        return True

    def stop_service(self, name):
        """
        :param name:
        :return:
        :param greenlet:
        :return:
        """

        if name in self._directory:
            self.log.info("stopping service [%s]..." % name)
            service = self._directory_service_proxy.get_service(name)

            if not service.ready():
                service.stop()
                self.log.info("service [%s] stopped." % name)
            else:
                self.log.info("service [%s] already stopped." % name)

            self._directory.pop(name)
            return True

        return False

    def stop_services(self):
        for pid_key, pid in self._directory.items():
            # pid.stop()
            self.stop_service(pid_key)

    def get_directory_service_proxy(self):
        return self._directory_service_proxy

    def get_service_count(self):
        return self._directory_service_proxy.get_service_count()

    def get_services(self):
        return self._directory.items()

    def get_service(self, service_id):
        return self.get_directory_service_proxy().get_service(service_id)


class Scheduler(BaseService):
    """
    The scheduler at this point is in charge of scheduling a service action
    with a local or group of service managers or a mix with remote service
    managers.

    I allowed the scheduler to schedule the start of services within the event
    loop, though having it on the service manager instead is an alternative. I
    will say that for now though since the service manager does not implement
    an event loop (easily could) I have left the code out from it.
    """
    def event_loop_next(self):
        return EventLoopStates(self.event_loop_state.next())._name_

    def __init__(self, name, parent_logger=None):
        BaseService.__init__(self, name, parent_logger=parent_logger)

        # workers each handle one rest endpoint
        self._service_manager = ServiceManager("service-manager", parent_logger=self.log)

        self.set_directory_service_proxy(self._service_manager.get_directory_service_proxy())

        self.event_loop_state = RoundRobinIndexer(2)
        self.log.debug("Initialized.")

    def event_loop(self):
        while self.should_loop():
            self.event_loop_next()
            # schedule the service manager to start designated services if any
            pids = self._service_manager._start_services()

            gevent.idle()

    def get_service_manager(self):
        return self._service_manager

    def add_service(self, service):
        """
        Calls service manager.
        :param service:
        :return:
        """
        return self._service_manager.add_service(service, service.alias)

    def stop_service(self, name):
        """
        Calls service manager.
        :param name:
        :return:
        """
        return self._service_manager.stop_service(name)

    def get_services(self):
        return self.get_service_manager().get_services()

    def get_services_count(self):
        return self._service_manager.get_service_count()

    def start(self):
        """
        Starts the scheduler, which by default starts
        the service manager. They work hand in hand.
        :return:
        """
        BaseService.start(self)
        self._service_manager.start()
        return self.greenlet

    def stop(self):
        """
        Stops the scheduler.
        :return:
        """
        self._service_manager.stop_services()
        self._service_manager.stop()
        BaseService.stop(self)

