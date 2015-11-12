from v2.system.services import BaseService
from v2.system.os import ServiceManager


def test_service_manager():
    manager = ServiceManager("service-manager-1")
    d1 = manager._directory
    assert d1 is not None

    # direct mod to directory allowed
    d1["test-1"] = 1
    assert manager.get_service_count() == 1

    d1.pop("test-1")
    assert manager.get_service_count() == 0


def test_add_service():
    manager = ServiceManager("service-manager-1")
    test_service = BaseService("test-1")

    # Add service
    assert manager.add_service(test_service, "test-1") == True

    # Add adding again should fail
    assert manager.add_service(test_service, "test-1") == False


def test_stop_service():
    manager = ServiceManager("service-manager-1")
    test_service = BaseService("test-1")

    # Add service
    assert manager.add_service(test_service, "test-1") == True
    assert manager.get_service_count() is 1

    # Stop
    assert manager.stop_service("test-1") == True
    assert manager.get_service_count() == 0

    # Stop Again will fail
    assert manager.stop_service("test-1") == False
