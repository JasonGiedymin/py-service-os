# external
import gevent

# lib
from v2.services.services import BaseService, ExecutorService
from v2.system.os import Scheduler

__author__ = 'jason'


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
        """
        Boots up the OS and any services which the scheduler has
        scheduled.
        :return:
        """
        self.log.info("booting up...")
        self.scheduler.start()
        self.set_directory_service_proxy(self.scheduler.get_directory_service_proxy())
        self.start()  # start self, as an executor service runs one pass and registers as successful

    def shutdown(self):
        self.log.info("shutting down...")
        self.scheduler.stop()
        self.stop()

    def schedule_service(self, service_class, service_meta, error_handlers=[]):
        """
        Take a service and let the instaniation begin here.
        :param service_class: python class to use
        :param service_meta: metadata about the service
        :param error_handlers: a list of error handlers which to execute
        :return:
        """
        service = service_class(service_meta.alias, parent_logger=self.log)
        service.add_error_handlers(error_handlers)
        self.scheduler.add_service_with_meta(service, service_meta)

    def schedule_provided_service(self, service):
        """
        SOON TO BE DEPRECATED.
        Take a service and schedules it as-is.
        Prefer not to use this method.
        :param service:
        :return:
        """
        self.scheduler.add_service(service)

    # def event_loop(self):
    #     """
    #     The event loop.
    #     """
    #     while self.should_loop():
    #         gevent.idle()
