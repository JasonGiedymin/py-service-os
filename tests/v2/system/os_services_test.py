# External

# Lib
from v2.services.services import BaseService
from v2.system.exceptions import IdleActionException, ServiceNotIdleException
from v2.system.os import Scheduler, ServiceManager
from v2.system.states import BaseStates

# Test helpers
from mock_services import TestWorker


def test_baseservice():
    """
    Base service tests for:
        - [x] name on init
        - [x] idle state on init
        - [x] starting state on start()
        - [x] ready() alias for idle state
        - [x] stopped state on stop()
        - [x] idle state exception when service not in stopped state
        - [x] idle state on idle()
    :return:
    """

    name = "base-service-1"
    base = BaseService(name)
    assert base.alias == name
    assert base.unique_name == '%s/%s' % (name, base.uuid)
    assert base.get_state() == BaseStates.Idle
    assert base.ready() is True  # ready == Idle

    greenlet = base.start()
    assert greenlet is not None
    assert base.get_state() == BaseStates.Starting
    assert base.ready() is False

    # exception should be thrown if state is started
    # and asking service to make itself idle.
    try:
        base.idle()
    except IdleActionException as ex:
        assert ex is not None

    base.stop()
    assert base.get_state() == BaseStates.Stopped

    # Try restarting the service, it will fail because it is not idle
    # In order to restart a service must be set to idle again.
    try:
        base.start()
    except ServiceNotIdleException as ex:
        assert ex is not None

    # now set to idle
    base.idle()  # should not throw this time
    assert base.get_state() == BaseStates.Idle

    # not start, should work and not throw an exception
    base.start()


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
    assert base.alias == name
    assert base.unique_name == '%s/%s' % (name, base.uuid)
    assert base.get_state() == BaseStates.Idle
    assert base.ready() is True  # ready == Idle

    greenlet = base.start()
    assert greenlet is not None
    assert base.get_state() == BaseStates.Starting
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


def test_scheduler():
    scheduler = Scheduler("scheduler")
    assert scheduler.get_services_count() == 0
    assert scheduler.get_state() == BaseStates.Idle

    scheduler.start()
    assert scheduler.get_state() == BaseStates.Starting

    scheduler.stop()
    assert scheduler.get_state() == BaseStates.Stopped

    scheduler.add_service(TestWorker("test-worker-1"))
    assert scheduler.get_services_count() == 1

    scheduler.add_service(TestWorker("test-worker-2"))
    assert scheduler.get_services_count() == 2


def test_directory_service():
    """
    Start test by getting the directory service
    via a ServiceManager.
    :return:
    """
    service_manager = ServiceManager("test-service-manager-1")
    directory_service = service_manager.get_directory_service_proxy()
    assert directory_service is not None
    assert directory_service.alias == "directory-service"
    assert directory_service.unique_name == '%s/%s' % ("directory-service", directory_service.uuid)
    assert directory_service.get_service_count() == 0
