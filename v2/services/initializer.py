# Lib
from v2.system.services import BaseService
# from v2.data.db import MemDB
# from v2.data.queue import MemQueue

# System
import gevent

__author__ = 'jason'


class InitializerService(BaseService):
    """
    Put resources into a queue.
    """
    def __init__(self, name, parent_logger=None):
        BaseService.__init__(self, name, parent_logger=parent_logger)
        self.current_batch = []
        self.db = None
        self.queue = None
        self.registered = {}  # simple dict keeping resources already registered

    def set_db(self, db):
        self.db = db

    def set_queue(self, queue):
        self.queue = queue

    def event_loop(self):
        """
        The event loop.
        """
        while True:
            for res_uri, res in self.db.get_resources():
                if res_uri not in self.registered:
                    self.queue.put_analyze(res)
                    self.registered[res_uri] = res
                    self.log.info("registered new resource, id:[%s], uri:[%s]" % (res.id, res_uri))
                # else:  # resource already exists
                    # if resource.reload:  # check if it needs reloading
                    #     self.registered.pop(resource.id)  # popping it will reload it next loop
                    #     self.log.debug("resource set to be reloaded, id:[%s], uri:[%s]" % (resource.id, resource.uri))

                gevent.idle()
