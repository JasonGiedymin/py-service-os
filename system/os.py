__author__ = 'jason'

# external
import gevent
from gevent.queue import Queue

# lib
from services import BaseService, DirectoryService
from states import BaseStates, EventLoopStates
from strategies import RoundRobinIndexer


class ServiceManager(BaseService):
    def __init__(self, name):
        BaseService.__init__(self, name)
        self._directory = {}
        self.started_services = Queue()
        self._directory_service_proxy = DirectoryService(self._directory)

    def start(self):
        BaseService.start(self)
        self._directory_service_proxy.start()

        print "starting services..."
        for service_name, service in self._directory.iteritems():
            print "starting service %s" % service_name
            self.started_services.put(service.start())

    def add_service(self, service, name):
        """
        Add service to service manager by name.
        :param greenlet:
        :param name:
        :return:
        """
        print "service %s added" % name
        service.set_directory_service_proxy(self._directory_service_proxy)
        self._directory[name] = service

    def stop_service(self, name):
        """
        :param greenlet:
        :return:
        """
        print "stopping services..."
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
    def event_loop_next(self):
        return EventLoopStates(self.event_loop_state.next())._name_

    def __init__(self, name):
        BaseService.__init__(self, name)
        self._service_manager = ServiceManager("service-manager")  # workers each handle one rest endpoint
        self.event_loop_state = RoundRobinIndexer(2)

    def event_loop(self):
        while self._service_state:
            # print "--> %s" % self.event_loop_next()
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
