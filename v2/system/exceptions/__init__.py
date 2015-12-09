__author__ = 'jason'


class IdleActionException(Exception):
    msg = "Service state is not in stopped state, cannot make idle unless service is first stopped."

    def __init__(self):
        Exception.__init__(self, self.msg)


class ServiceNotIdleException(Exception):
    msg = "Service is not in idle state, put service in idle state via `service.idle()` in order to restart it."

    def __init__(self):
        Exception.__init__(self, self.msg)
