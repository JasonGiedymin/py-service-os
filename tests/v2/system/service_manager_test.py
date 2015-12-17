from v2.system.services import BaseService
from v2.system.os import ServiceManager
from v2.data.simple_data import ServiceMetaData

def test_service_manager():
    manager = ServiceManager("service-manager-1")
    d1 = manager.service_directory
    assert d1 is not None

    # direct mod to directory allowed
    d1["test-1"] = 1
    assert manager.get_service_count() == 1

    d1.pop("test-1")
    assert manager.get_service_count() == 0


def test_add_service():
    service_alias = "test-1"
    manager = ServiceManager("service-manager-1")
    service_meta = ServiceMetaData(service_alias)
    test_service = BaseService(service_meta.alias)

    # Add service

    assert manager.add_service(test_service, service_meta) == True

    # Add adding again should fail
    assert manager.add_service(test_service, service_meta) == False


def test_stop_service():
    service_alias = "test-1"
    manager = ServiceManager("service-manager-1")
    service_meta = ServiceMetaData(service_alias)
    test_service = BaseService(service_meta.alias)

    # Add service
    assert manager.add_service(test_service, service_meta) == True
    assert manager.get_service_count() is 1

    # Stop
    assert manager.stop_service(service_alias) == True
    assert manager.get_service_count() == 0

    # Stop Again will fail
    assert manager.stop_service(service_alias) == False
