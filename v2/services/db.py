# Lib
from v2.data.db import BaseDB, MemDB
from v2.services.services import BaseService

# System

__author__ = 'jason'


class DBService(BaseDB, BaseService):
    """
    Database service proxy.
    """
    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        BaseService.__init__(self, name, parent_logger=parent_logger, enable_service_recovery=enable_service_recovery)
        self.db = MemDB()  # db implementation

    # below methods are proxies to the db interface
    def save_resource_with_key(self, resource, key):
        self.db.save_resource_with_key(resource, key)

    def save_resource(self, resource):
        self.db.save_resource(resource)

    def get_resource(self, key):
        return self.db.get_resource(key)

    def get_resources(self):
        return self.db.get_resources()

    def update_resource(self, resource, key):
        return self.db.update_resource(resource, key)

    def resource_count(self):
        return self.db.resource_count()
