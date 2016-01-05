# External
import time

import gevent
# Lib
from v2.system.os import Scheduler
from v2.services.services import BaseService
from v2.system.states import BaseStates

# Test helpers
from mock_services import MockQueuedService, TestWorker


# Global vars
worker_interval = .5
scheduler_interval = worker_interval + 1


# A timer that will trigger and call stop on the scheduler
class Timer(BaseService):
    def __init__(self, service, mock_output_pid):
        BaseService.__init__(self, "timer")
        self.service = service
        self.mock_output_pid = mock_output_pid

    def event_loop(self):
        gevent.sleep(scheduler_interval)
        # essentially doing what a service manager is doing
        # note: stop doing tests like this, use a canned os instead
        self.mock_output_pid.stop()
        self.mock_output_pid.idle()
        self.service.stop()


def test_os():
    """
    At this point we've tested BaseService, so I expect
    the following to work.

    Note: It is now prudent to leave this test or slowly invalidate it
          and instead use the CannedOS. See
          `v2/services/freezer_services_test.py` as an example

    :return:
    """

    scheduler = Scheduler("scheduler")

    # create services
    test_worker_1 = TestWorker("test-worker-1", worker_interval)
    test_worker_2 = TestWorker("test-worker-2", worker_interval)
    mock_queue_service = MockQueuedService()

    # schedule services
    scheduler.add_service(test_worker_1)
    scheduler.add_service(test_worker_2)
    scheduler.add_service(mock_queue_service)
    assert scheduler.get_services_count() == 3

    # test for existence of a service manager
    assert scheduler.get_service_manager() is not None

    # test that a child worker has access to the service_manager proxy
    test_worker_1_service = scheduler.get_service_manager().get_directory_service_proxy().get_service("test-worker-1")
    assert test_worker_1_service is not None
    # assert that the service is exactly as what was started
    assert test_worker_1_service == test_worker_1

    # assert that the service has a reference to the directory proxy
    directory_proxy = test_worker_1.get_directory_service_proxy()
    assert directory_proxy is not None
    assert directory_proxy.get_service_count() == 3

    # assert all the same all around
    assert directory_proxy.get_service("test-worker-1") == test_worker_1_service

    # direct check to make sure
    assert directory_proxy._service_manager_directory == scheduler.get_service_manager().service_directory

    # start test timer
    timer = Timer(scheduler, mock_output_pid=mock_queue_service)

    # take timing from start to finish
    t1 = time.time()
    gevent.joinall([scheduler.start(), timer.start()])  # blocks

    t2 = time.time()
    t3 = t2 - t1
    assert t3 > scheduler_interval

    # stop was called, check all states
    assert scheduler.get_service_manager().get_state() == BaseStates.Stopped
    assert scheduler.get_state() == BaseStates.Stopped
    for pid_key, pid in scheduler.get_services():
        assert pid.get_state() == BaseStates.Stopped

