__author__ = 'jason'


class IdleActionException(Exception):
    msg = "Service state is not in stopped state, cannot make idle unless service is first stopped."

    def __init__(self):
        Exception.__init__(self, self.msg)


class ServiceNotIdleException(Exception):
    msg = "Service is not in idle state, put service in idle state via `service.idle()` in order to restart it."

    def __init__(self):
        Exception.__init__(self, self.msg)


class ServiceMetaDataNotFound(Exception):
    msg = "A service's metadata could not be found! This is a grave error and this OS may shutdown!"

    def __init__(self):
        Exception.__init__(self, self.msg)


class ServiceException(Exception):
    msg = "A service has raised an exception or an error was detected! Inner error: [%s]"

    def __init__(self, inner_error):
        Exception.__init__(self, self.msg % inner_error)


class HandlerException(Exception):
    msg = "A handler has raised an exception or an error was detected! Inner error: [%s]"

    def __init__(self, inner_error):
        Exception.__init__(self, self.msg % inner_error)

