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
        self.set_directory_service_proxy(self._directory_service_proxy)  # since BaseService declares an interface

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
            pid.stop()

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
        while self._service_state:
            self.event_loop_next()
            # gevent.sleep(.5)
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
        Starts the scheduler.
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

