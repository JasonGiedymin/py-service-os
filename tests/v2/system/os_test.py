# External
import time
import gevent

# Lib
from v2.system.os import Scheduler, ServiceManager
from v2.system.services import BaseService, OutputService
from v2.system.states import BaseStates
from v2.system.exceptions import IdleActionException

# Test helpers
from mock_services import MockOutputService, TestWorker


def test_baseservice():
    """
    Base service tests for:
        - [x] name on init
        - [x] idle state on init
        - [x] started state on start()
        - [x] ready() alias for idle state
        - [x] stopped state on stop()
        - [x] idle state exception when service not in stopped state
        - [x] idle state on idle()
    :return:
    """

    name = "base-service-1"
    base = BaseService(name)
    assert base.name == name
    assert base.get_state() == BaseStates.Idle
    assert base.ready() is True  # ready == Idle

    greenlet = base.start()
    assert greenlet is not None
    assert base.get_state() == BaseStates.Started
    assert base.ready() is False

    # exception should be thrown if state is started
    # and asking service to make itself idle.
    try:
        base.idle()
    except IdleActionException as ex:
        assert ex is not None

    base.stop()
    assert base.get_state() == BaseStates.Stopped
    base.idle()  # should not throw this time
    assert base.get_state() == BaseStates.Idle


def test_baseservice_service_directory():
    """
    Base service tests for:
        - [x] name on init
        - [x] idle state on init
        - [x] started state on start()
        - [x] ready() alias for idle state
        - [x] stopped state on stop()
        - [x] idle state exception when service not in stopped state
        - [x] idle state on idle()
    :return:
    """

    name = "base-service-1"
    base = BaseService(name)
    assert base.name == name
    assert base.get_state() == BaseStates.Idle
    assert base.ready() is True  # ready == Idle

    greenlet = base.start()
    assert greenlet is not None
    assert base.get_state() == BaseStates.Started
    assert base.ready() is False

    # exception should be thrown if state is started
    # and asking service to make itself idle.
    try:
        base.idle()
    except IdleActionException as ex:
        assert ex is not None

    base.stop()
    assert base.get_state() == BaseStates.Stopped
    base.idle()  # should not throw this time
    assert base.get_state() == BaseStates.Idle


def test_output_service():
    # Test Output service class
    output = OutputService("out-1")
    assert output is not None

    output.put("1")
    assert output.size() == 1

    val = output.get()
    assert val == "1"
    assert output.size() == 0


def test_output_service_loop():
    mock_output_service = MockOutputService()

    # join and block, waiting for event loop to execute once
    # and then exits. Mock manually controls the event loop.
    gevent.joinall([mock_output_service.start()])
    assert mock_output_service.event_loop_ack is True
    assert mock_output_service.get_state() == BaseStates.Idle


def test_output_service_write():
    # create ServiceManager and add services
    service_manager = ServiceManager("service-manager")

    # add worker
    worker_name = "test-worker-1"
    test_worker_1 = TestWorker(worker_name)
    service_manager.add_service(test_worker_1, worker_name)

    # add output service
    mock_output_service = MockOutputService()
    service_manager.add_service(mock_output_service, "mock-output-service")

    assert test_worker_1.get_state() == BaseStates.Idle
    assert mock_output_service.get_state() == BaseStates.Idle

    # join and block, waiting for event loop to execute once
    # and then exits. Mock manually controls the event loop.
    # Manually starting services rather than using service_manager
    gevent.joinall([test_worker_1.start(), mock_output_service.start()])

    # Assert that state is started. State will not be stopped
    # or idle because the services were manually called. Except
    # for the Mock service which will be idle. See the code.
    assert test_worker_1.get_state() == BaseStates.Started
    assert mock_output_service.get_state() == BaseStates.Idle

    # the services ran and I expect the test worker to have queried
    # the directory proxy and found the output service, writing to it.
    result = mock_output_service.get()
    assert result is not None
    assert result == "test-worker-work-result"
    assert mock_output_service.size() == 0


def test_scheduler():
    scheduler = Scheduler("scheduler")
    assert scheduler.get_services_count() == 0
    assert scheduler.get_state() == BaseStates.Idle

    scheduler.start()
    assert scheduler.get_state() == BaseStates.Started

    scheduler.stop()
    assert scheduler.get_state() == BaseStates.Stopped

    scheduler.add_service(TestWorker("test-worker-1"))
    assert scheduler.get_services_count() == 1

    scheduler.add_service(TestWorker("test-worker-2"))
    assert scheduler.get_services_count() == 2


def test_service_manager():
    manager = ServiceManager("service-manager-1")
    d1 = manager._directory
    assert d1 is not None

    # direct mod to directory allowed
    d1["test-1"] = 1
    assert manager.get_service_count() == 1

    d1.pop("test-1")
    assert manager.get_service_count() == 0


def test_directory_service():
    """
    Start test by getting the directory service
    via a ServiceManager.
    :return:
    """
    service_manager = ServiceManager("test-service-manager-1")
    directory_service = service_manager.get_directory_service_proxy()
    assert directory_service is not None
    assert directory_service.name == "directory-service"
    assert directory_service.get_service_count() == 0


def test_os():
    """
    At this point we've tested BaseService, so I expect
    the following to work.
    :return:
    """
    worker_interval = .5
    scheduler_interval = 2

    # A timer that will trigger and call stop on the scheduler
    class Timer(BaseService):
        def __init__(self, service):
            BaseService.__init__(self, "timer")
            self.service = service

        def event_loop(self):
            gevent.sleep(scheduler_interval)
            # gevent.kill(self.service.get_greenlet())
            self.service.stop()

    class TestOutputService(OutputService):
        def __init__(self):
            OutputService.__init__(self, "mock-output-service")
            self.event_loop_ack = False

        def event_loop(self):
            gevent.sleep(.1)
            self.event_loop_ack = True
            # this service will stop as the end of the event loop has been reached
            self.set_state(BaseStates.Stopped)
            self.idle()

    scheduler = Scheduler("scheduler")

    # add services
    test_worker_1 = TestWorker("test-worker-1", worker_interval)
    scheduler.add_service(test_worker_1)
    scheduler.add_service(TestWorker("test-worker-2", worker_interval))
    scheduler.add_service(TestOutputService())
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
    assert directory_proxy._service_manager_directory == scheduler.get_service_manager()._directory

    # start test timer
    timer = Timer(scheduler)

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

