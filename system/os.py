__author__ = 'jason'

# external
import gevent
from gevent.queue import Queue

# lib
from services import BaseService
from states import BaseStates, EventLoopStates
from strategies import RoundRobinIndexer


class ServiceManager(BaseService):
    def __init__(self, name):
        BaseService.__init__(self, name)
        self.directory = {}
        self.started_services = Queue()

    def start(self):
        BaseService.start(self)

        print "starting services..."
        for service_name, service in self.directory.iteritems():
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
        self.directory[name] = service

    def stop_service(self, name):
        """
        :param greenlet:
        :return:
        """
        service = self.directory.get(name)
        gevent.kill(service)
        self.directory.pop(service)


class Scheduler(BaseService):
    def event_loop_next(self):
        return EventLoopStates(self.event_loop_state.next())._name_

    def __init__(self, name):
        BaseService.__init__(self, name)
        self.service_manager = ServiceManager("service-manager")  # workers each handle one rest endpoint
        self.event_loop_state = RoundRobinIndexer(2)

    def event_loop(self):
        while self.service_state:
            print "--> %s" % self.event_loop_next()
            gevent.sleep(.5)

    def add_service(self, service):
        self.service_manager.add_service(service, service.name)

    def start(self):
        BaseService.start(self)
        self.service_manager.start()
        return self.greenlet

# scheduler = Scheduler("scheduler")
# scheduler.add_service(TestWorker("test-worker-1"))
# scheduler.add_service(TestWorker("test-worker-2"))
# gevent.joinall([scheduler.start()])
