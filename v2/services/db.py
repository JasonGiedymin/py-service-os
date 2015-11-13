# Lib
from v2.system.services import BaseService
from v2.data.db import BaseDB, MemDB

# System
import gevent

__author__ = 'jason'


class DBService(BaseService, BaseDB):
    """
    Database service proxy.
    """
    def __init__(self, name, parent_logger=None):
        BaseService.__init__(self, name, parent_logger=parent_logger)
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

    def event_loop(self):
        """
        The event loop.
        """
        gevent.idle()
