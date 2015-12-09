# Lib
from v2.system.services import BaseService

# System
import gevent

__author__ = 'jason'


class ClusterAgent(BaseService):
    """
    Cluster Agent will work communicate with a cluster kv store
    for configuration information.
    """
    def __init__(self, name, parent_logger=None):
        BaseService.__init__(self, name, parent_logger=parent_logger)

    def event_loop(self):
        """
        The event loop.
        """
        while True:
            self.log.debug("working....")
            gevent.sleep(1)
