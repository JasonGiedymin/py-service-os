from abc import ABCMeta, abstractmethod


class BaseDB(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def save_resource(self, resource, key):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def get_resource(self, key):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def update_resource(self, resource, key):
        raise NotImplementedError("Please Implement this method")


class MemDB(BaseDB):
    """
    In memory DB, not optimized, not persistent.
    Use as a testing tool.
    Can also be used as a cache for test.
    """
    def __init__(self):
        self.resources = {}

    def save_resource_with_key(self, resource, key):
        self.resources[key] = resource

    def save_resource(self, resource):
        key = resource.uri
        self.resources[key] = resource

    def get_resource(self, key):
        if key in self.resources:
            return self.resources.get(key)
        else:
            return None

    def get_resources(self):
        return self.resources.iteritems()

    def update_resource(self, resource, key):
        return self.save_resource(resource, key)
