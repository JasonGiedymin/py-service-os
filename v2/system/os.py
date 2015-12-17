# external
import gevent
from greplin import scales

# lib
from v2.system.exceptions import ServiceMetaDataNotFound
from v2.system.services import BaseService, DirectoryService
from v2.system.strategies import RoundRobinIndexer
from v2.data.simple_data import ServiceMetaData, ServiceDirectoryEntry

__author__ = 'jason'


class ServiceManager(BaseService):
    """
    ServiceManager is in charge of starting or stopping services.
    """
    family_latency = scales.HistogramAggregationStat('latency')

    def __init__(self, name, parent_logger=None):
        scales.init(self, '/service-manager')
        BaseService.__init__(self, name, parent_logger=parent_logger)
        self.service_directory = {}

        self.directory_service_proxy = DirectoryService(self.service_directory, parent_logger=self.log)

        # BaseService declares an interface to the directory proxy
        # we continue to do this (just like any other service uses
        # the directory proxy. It is a bit recursive, but done for
        # completeness sake. This is just another reference
        # designated by the BaseService parent class.
        self.set_directory_service_proxy(self.directory_service_proxy)

    def _start_services(self):
        """
        Starts all designated services from the internal directory.

        A service once stopped is removed from this directory and that
        prevents it from starting back up again.

        A service is checked whether it is in a good state, and if not
        is allowed to restart if designated.

        A service can be flagged with bury if it is dead.

        TODO: The scheduler maintains a retry threshold for each
              service. That is if a service is found to have been
              restarted upto this threshold then it will no longer
              be restarted. This is to prevent concurrent fast
              restarts which will bog the system and is usually a
              sign of an issue. Note that the scheduler maintains
              a service start delay as well for each service.
        :return:
        """
        started_services = 0

        def startable(service_entry):
            return service_entry.service.ready() \
                   and not service_entry.service.has_started() \
                   # and not service.is_truly_dead()

        def recoverable(service_entry):
            return service_entry.service.is_zombie() \
                   and service_entry.service_meta.recovery_enabled \
                   # and not service.is_truly_dead()

        def start_service(incoming_service):
                pid = incoming_service.start()
                if pid is not None:
                    return 1
                else:
                    return 0

        for service_name, entry in self.service_directory.iteritems():
            if entry.service_meta is None:
                self.log.fatal("Could not find service metadata for service: [%s]" % (
                    service_name
                ), id=entry.service.unique_name, lineage=entry.service.lineage)
                raise ServiceMetaDataNotFound

            if startable(entry):
                self.log.info("starting service %s" % service_name)
                started_services += start_service(entry.service)
            elif recoverable(entry):
                # if a service is able to be recovered we must put it in the idle state
                entry.service.idle()
                self.log.info("recovering and restarting possible zombied service: [%s]" % service_name)
                started_services += start_service(entry.service)

        if started_services > 0:
            self.log.debug("started [%d] services in one event loop" % started_services)

        return started_services

    def start(self):
        BaseService.start(self)
        self.directory_service_proxy.start()

        self.log.info("starting services...")
        self._start_services()

        return self.greenlet

    def add_service(self, service, service_meta):
        """
        Add service to service manager by name.
        :param service: the actual service
        :param service_meta: metadata about the service
        :return:
        """
        self.log.debug("service %s added" % service_meta.alias)
        service.set_directory_service_proxy(self.directory_service_proxy)
        service.register()  # trigger and registration of data

        if service_meta.alias in self.service_directory:
            self.log.warn("service [%s] already exists" % service_meta.alias)
            return False

        entry = ServiceDirectoryEntry(service, service_meta)
        self.service_directory[service_meta.alias] = entry  # record the service, aka the pid
        return True

    def stop_service(self, alias):
        """
        :param alias:
        :return:
        :param greenlet:
        :return:
        """

        if alias in self.service_directory:
            self.log.info("stopping service [%s]..." % alias)
            service = self.directory_service_proxy.get_service(alias)

            if not service.ready():
                service.stop()
                self.log.info("service [%s] stopped." % alias)
            else:
                self.log.info("service [%s] already stopped." % alias)

            self.service_directory.pop(alias)
            return True

        return False

    def stop_services(self):
        for pid_key, pid in self.service_directory.items():
            # yes this method below will be O(2n), but we reuse methods.
            self.stop_service(pid_key)

    def get_directory_service_proxy(self):
        return self.directory_service_proxy

    def get_service_count(self):
        return self.directory_service_proxy.get_service_count()

    def get_services(self):
        return self.service_directory.items()

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
    # def event_loop_next(self):
    #     return EventLoopStates(self.event_loop_state.next())._name_

    def __init__(self, name, parent_logger=None):
        BaseService.__init__(self, name, parent_logger=parent_logger)

        # workers each handle one rest endpoint
        self.service_manager = ServiceManager("service-manager", parent_logger=self.log)

        self.set_directory_service_proxy(self.service_manager.get_directory_service_proxy())

        self.event_loop_state = RoundRobinIndexer(2)
        self.log.debug("Initialized.")

    def event_loop(self):
        while self.should_loop():
            # self.event_loop_next()
            # schedule the service manager to start designated services if any
            pids = self.service_manager._start_services()

            gevent.idle()

    def get_service_manager(self):
        return self.service_manager

    def add_service(self, service):
        """
        Older method where there was no interaction with the service meta data.
        Calls service manager with a default meta info about the service.
        :param service:
        :return:
        """
        service_meta = ServiceMetaData(service.alias, recovery_enabled=False)
        return self.service_manager.add_service(service, service_meta)

    def add_service_with_meta(self, service, service_meta):
        """
        Older method where there was no interaction with the service meta data.
        Calls service manager with a default meta info about the service.
        :param service: the service
        :param service_meta: the metadata about the service
        :return:
        """
        return self.service_manager.add_service(service, service_meta)

    def stop_service(self, name):
        """
        Calls service manager.
        :param name:
        :return:
        """
        return self.service_manager.stop_service(name)

    def get_services(self):
        return self.get_service_manager().get_services()

    def get_services_count(self):
        return self.service_manager.get_service_count()

    def start(self):
        """
        Starts the scheduler, which by default starts
        the service manager. They work hand in hand.
        :return:
        """
        BaseService.start(self)
        self.service_manager.start()
        return self.greenlet

    def stop(self):
        """
        Stops the scheduler.
        :return:
        """
        self.service_manager.stop_services()
        self.service_manager.stop()
        BaseService.stop(self)

