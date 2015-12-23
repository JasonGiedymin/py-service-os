# external
import gevent
from greplin import scales

# lib
from v2.system.exceptions import ServiceMetaDataNotFound, ServiceNotIdleException
from v2.services.services import BaseService, DirectoryService
from v2.system.states import BaseStates
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

    def start_service(self, alias):
        entry = self.get_service_entry(alias)

        if entry is None:
            self.log.error("Could not find an entry for service named: [%s]" % alias)
            return 0

        def startable(service_entry):
            """
            Checks to see if a service is startable. Can't start something which
            has already started.
            :param service_entry:
            :return:
            """
            return (service_entry.service.ready() and
                    not service_entry.service.has_started())

        def recoverable(service_entry):
            """
            A recoverable service is one which is a zombie (has no BaseService state)
            as if it was lost and re-created by some means or never updated properly.
            Either way, check if it has recovery so that it may be brought back to a
            legit life.
            :param service_entry:
            :return:
            """
            return (service_entry.service.is_zombie() and
                    service_entry.service_meta.recovery_enabled)

        def resurrectable(service_entry):
            """
            A resurrectable service is one which is truely dead but is allowed to be
            brought back to life.
            :param service_entry:
            :return:
            """
            return (service_entry.service.is_truly_dead() and
                    service_entry.service_meta.recovery_enabled)

        def start(service_entry):
            """
            Start a service based on a service entry from the directory.
            Will always apply the service delay if it is available.
            :param service_entry:
            :return:
            """
            if service_entry.service.get_state() is BaseStates.Starting:
                # this service is starting up...
                # TODO: here examine if it reached a start timeout or something, cause it could go wrong
                return 0

            # only start if retries have not been reached, exit
            # immediately
            if service_entry.service_meta.retry_limit_reached():
                retries = service_entry.service_meta.retries
                self.log.debug("retry limit [%d] reached for service" % retries,
                               service_alias=service_entry.service_meta.alias)
                return 0

            pid = None

            try:
                pid = service_entry.service.start(service_entry.service_meta.delay)
            except ServiceNotIdleException as service_ex:
                # TODO: use the finite exception in the future
                service_entry.service.handle_error()
            except Exception as ex:
                # TODO: use the finite exception in the future
                service_entry.service.handle_error()

            service_entry.service_meta.starts += 1

            if pid is not None:
                return 1
            else:
                return 0

        if entry.service_meta is None:
            self.log.fatal("Could not find service metadata for service: [%s]" % (
                entry.alias
            ), id=entry.service.unique_name, lineage=entry.service.lineage)
            raise ServiceMetaDataNotFound

        # complete dead services have priority, higher in the evaluation, exit fast, detect fast
        if resurrectable(entry):
            self.log.info("service [%s] was found dead considering to be resurrected..." % entry.service_meta.alias,
                          service_alias=entry.service_meta.alias)
            ex = entry.service.greenlet.exception
            if ex is not None:
                entry.service_meta.exceptions.append(entry.service.greenlet.exception)
            return start(entry)
        elif startable(entry):
            self.log.info("executing service start for [%s]" % entry.service_meta.alias,
                          service_alias=entry.service_meta.alias)
            return start(entry)
        elif recoverable(entry):
            # if a service is able to be recovered we must put it in the idle state
            entry.service.idle()
            self.log.info("recovering and restarting possible zombied service: [%s]" % entry.service_meta.alias)
            return start(entry)
        else:  # if already started perhaps, and not a zombie do nothing.
            return 0

    def monitor_services(self):
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

        for alias, entry in self.service_directory.iteritems():
            started_services += self.start_service(alias)

        if started_services > 0:
            self.log.debug("started [%d] services in one event loop" % started_services)

        return started_services

    def start(self):
        BaseService.start(self)
        self.directory_service_proxy.start()

        self.log.info("starting services...")
        self.monitor_services()

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

    def stop_service_pid(self, service, halt=False):
        """
        This stops a specific service. A service may be halted if flagged. It is however expected that
        the service will be immediately restarted shortly! Else it will get auto restarted! Usually
        this method allows fine grained actions to occur within the scope of a single event loop.
        Again, otherwise services may be recovered in the next loop.

        :param service: the actual service.
        :param halt: True if the service should be halted, False otherwise. A halted service is one which retains
                     an entry within the directory service. Usually meant for a service which will restart very
                     soon.
        :return: True if stopped, False otherwise.
        """

        def stop(incoming_service):
            self.log.info("stopping service [%s]..." % incoming_service.alias)

            if not incoming_service.ready():
                incoming_service.stop()
                self.log.info("service [%s] stopped." % incoming_service.alias)
            else:
                self.log.info("service [%s] already stopped." % incoming_service.alias)

            if not halt:
                self.service_directory.pop(incoming_service.alias)

            return True

        return stop(service)

    def stop_service(self, alias, halt=False):
        """
        :param alias:
        :param halt: True if the service should be halted, False otherwise. A halted service is one which retains
                     an entry within the directory service. Usually meant for a service which will restart very
                     soon.
        :return:
        """

        if alias in self.service_directory:
            service = self.directory_service_proxy.get_service(alias)
            return self.stop_service_pid(service, halt=halt)

        self.log.error("Could not find service named [%s] to stop." % alias)
        return False

    def restart_service(self, alias):
        self.log.info("Attempting restart of service: [%s]" % alias, service_alias=alias)
        if self.stop_service(alias, halt=True):  # service was able to be stopped
            if self.start_service(alias) > 0:  # service was able to be started
                self.log.info("Service [%s] restarted successfully" % alias, service_alias=alias)
                return True
            else:  # service was not able to be started for whatever reason
                self.log.error("Service [%s] could not be restarted" % alias, service_alias=alias)
                return False
        else:  # service could not be stopped for whatever reason
            self.log.error("Service [%s] restart failed" % alias, service_alias=alias)

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

    def get_service(self, alias):
        return self.get_directory_service_proxy().get_service(alias)

    def get_service_meta(self, alias):
        return self.get_directory_service_proxy().get_service_meta(alias)

    def get_service_entry(self, alias):
        return self.get_directory_service_proxy().get_service_entry(alias)


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
            pids = self.service_manager.monitor_services()

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

    def stop_service(self, alias):
        """
        Calls service manager.
        :param alias:
        :return:
        """
        return self.service_manager.stop_service(alias)

    def start_service(self, alias):
        """
        Calls service manager.
        :param alias:
        :return:
        """
        return self.service_manager.start_service(alias)

    def restart_service(self, alias):
        return self.service_manager.restart_service(alias)

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

