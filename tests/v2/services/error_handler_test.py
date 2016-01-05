from v2.data.simple_data import ServiceDirectoryEntry
from v2.data.simple_data import ServiceMetaData
from v2.services.error_handler import ErrorHandler, ErrorHandlerMixin, ErrorHandlerFactory
from v2.services.services import ExecutorService, DirectoryService
from v2.system.exceptions import HandlerException

# Test libs

# Global vars
worker_interval = .5
scheduler_interval = worker_interval + 1
os_stop_time = 10


class E1(ErrorHandler):
    def next(self, service_meta):
        """
        Basic verify that this method was called, use the service meta exception
        list. Not that this is not how you should use the list, I am only using
        it as it makes it convenient to use.
        :param service_meta:
        :return:
        """
        service_meta.exceptions.append("Exception E1 Handled...")
        return service_meta


class E2(ErrorHandler):
    def next(self, service_meta):
        """
        Basic verify that this method was called, use the service meta exception
        list. Not that this is not how you should use the list, I am only using
        it as it makes it convenient to use.
        :param service_meta:
        :return:
        """
        service_meta.exceptions.append("Exception E2 Handled...")
        return service_meta


class E3(ErrorHandler):
    def next(self, service_meta):
        self.log.debug("test 1 2 3")
        raise Exception("Fake Error!")


class MockSimpleService(ErrorHandlerMixin, ExecutorService):
    def __init__(self, alias):
        ExecutorService.__init__(self, alias)
        ErrorHandlerMixin.__init__(self)


def test_no_handlers():
    service_alias = "mock-simple-service"
    service = MockSimpleService(service_alias)
    meta = ServiceMetaData(service_alias)
    service_entry = ServiceDirectoryEntry(service, meta)

    # for the purpose of this test add a directory (something which is done
    # for us in a CannedOS
    directory = {meta.alias: service_entry}
    directory_proxy = DirectoryService(directory)
    service.set_directory_service_proxy(directory_proxy)

    # run the handlers which in this case, are none
    service.handle_error()

    assert len(meta.exceptions) == 0


def test_error_handler():
    """
    Simple test that ensures the error handler works as expected.
    Exceptions are not caught here. See `test_error_handler_exception`
    for that.
    :return:
    """
    service_alias = "mock-simple-service"
    service = MockSimpleService(service_alias)
    meta = ServiceMetaData(service_alias)
    service_entry = ServiceDirectoryEntry(service, meta)

    # for the purpose of this test add a directory (something which is done
    # for us in a CannedOS
    directory = {meta.alias: service_entry}
    directory_proxy = DirectoryService(directory)
    service.set_directory_service_proxy(directory_proxy)

    # expect that these two handlers are run, which will append
    # text to the exceptions list in the metadata of the service
    # entry meta object.
    e1 = ErrorHandlerFactory.create(E1, service)
    e2 = ErrorHandlerFactory.create(E2, service)

    service.add_error_handler(e1)
    service.add_error_handler(e2)
    # run the handlers
    service.handle_error()

    assert len(meta.exceptions) == 2
    assert meta.exceptions[0] == "Exception E1 Handled..."
    assert meta.exceptions[1] == "Exception E2 Handled..."


def test_error_handler_exception():
    service_alias = "mock-simple-service"
    service = MockSimpleService(service_alias)
    meta = ServiceMetaData(service_alias)
    service_entry = ServiceDirectoryEntry(service, meta)

    # for the purpose of this test add a directory (something which is done
    # for us in a CannedOS
    directory = {meta.alias: service_entry}
    directory_proxy = DirectoryService(directory)
    service.set_directory_service_proxy(directory_proxy)

    # expect that these two handlers are run, which will append
    # text to the exceptions list in the metadata of the service
    # entry meta object.
    service.add_error_handler(ErrorHandlerFactory.create(E1, service))
    service.add_error_handler(ErrorHandlerFactory.create(E2, service))
    service.add_error_handler(ErrorHandlerFactory.create(E3, service))

    try:
        # run the handlers
        service.handle_error()
    except HandlerException as ex:
        print("Found exception for test, test passed as it was expected. Exception: [%s]" % ex)
