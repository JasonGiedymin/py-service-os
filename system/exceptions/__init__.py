__author__ = 'jason'


class IdleActionException(Exception):
    msg = "Service state is not in stopped, cannot make idle unless service is first stopped."

    def __init__(self):
        Exception.__init__(self, self.msg)
