# External
import time
import gevent

# Lib
from v2.system.canned_os import CannedOS
from v2.services.error_handler import ErrorHandler
from v2.system.exceptions import ServiceException

# Global vars
os_stop_time = 2


class MockErrorHandler(ErrorHandler):
    def __init__(self):
        ErrorHandler.__init__(self)

    def next(self, service_meta, exception):
        self.log.error("MOCK EXCEPTION TEST! - %s" % exception.message)
        return service_meta


class BadOS(CannedOS):
    def __init__(self, name):
        CannedOS.__init__(self, name)

    def event_loop(self):
        raise ServiceException("manual OS error - error 123 - seeing this is good!")

    def post_handle_error(self, exception):
        self.log.info("SHUTDOWN ISSUED - Post Handle Error called!")
        self.shutdown()


def test_services_for_exceptions():
    """
    This test simulates the RuntimeError "maximum recursion depth exceeded".
    Ensure that this test passes without seeing this error.
    :return:
    """
    error_handlers = [MockErrorHandler]
    os = BadOS("CannedOS")
    os.add_error_handlers(error_handlers)
    os.bootup()

    def stop_os():
        assert os.has_stopped() is True
        os.shutdown()  # this command should execute without failure

    # take timing from start to finish
    t1 = time.time()

    os_greenlet = gevent.spawn_later(os_stop_time, stop_os)
    gevent.joinall([os_greenlet])

    # == Test Validation/Verification ==
    # Makes sure that the test timer works correctly
    t2 = time.time()
    t3 = t2 - t1
    assert t3 > os_stop_time

    assert os_greenlet.successful()
