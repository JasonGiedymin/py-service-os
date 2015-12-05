# External
import gevent

# Lib
from v2.system.os import Scheduler, ServiceManager
from v2.system.services import BaseService, QueuedService
from v2.system.states import BaseStates

# Test helpers
from mock_services import MockQueuedService, TestWorker


# Global vars
scheduler_interval = 2


# A timer that will trigger and call stop on the scheduler
class Timer(BaseService):
    def __init__(self, service, mock_output_pid):
        BaseService.__init__(self, "timer")
        self.service = service
        self.mock_output_pid = mock_output_pid

    def event_loop(self):
        gevent.sleep(scheduler_interval)
        # gevent.kill(self.service.get_greenlet())
        # essentially doing what a service manager is doing
        # note: stop doing tests like this, use a canned os instead
        self.mock_output_pid.stop()
        self.mock_output_pid.idle()
        self.service.stop()


def test_output_service():
    # Test Output service class
    output = QueuedService("out-1")
    assert output is not None

    output.put("1")
    assert output.size() == 1

    val = output.get()
    assert val == "1"
    assert output.size() == 0


def test_output_service_loop():
    scheduler = Scheduler("scheduler")
    mock_output_service = MockQueuedService(quick_death=True)
    timer = Timer(scheduler, mock_output_pid=mock_output_service)

    # join and block, waiting for event loop to execute once
    # and then exits. Mock manually controls the event loop.
    gevent.joinall([mock_output_service.start(), timer.start()])
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
    scheduler = Scheduler("scheduler")
    mock_output_service = MockQueuedService(quick_death=True)
    timer = Timer(scheduler, mock_output_pid=mock_output_service)
    service_manager.add_service(mock_output_service, "mock-output-service")

    assert test_worker_1.get_state() == BaseStates.Idle
    assert mock_output_service.get_state() == BaseStates.Idle

    # join and block, waiting for event loop to execute once
    # and then exits. Mock manually controls the event loop.
    # Manually starting services rather than using service_manager
    gevent.joinall([test_worker_1.start(), mock_output_service.start(), timer.start()])

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
