# import requests
#
# session = requests.Session()
# session.headers = {
#     'User-Agent': 'DevStats-Machine',
#     'Authorization': 'token c0698ac78b8f29412f9a358bacd2d34711cdf217'
# }
# resp = session.get("https://api.github.com/events")
#
# with_etag = {
#     "If-None-Match": '%s' % resp.headers.get('ETag')
# }
#
# session.headers.update(with_etag)
#
# resp = session.get("https://api.github.com/events")
#
# print resp.status_code
# print resp.content

# Lib
from v2.system.services import BaseService
# from v2.data.db import MemDB
# from v2.data.queue import MemQueue

# System
import gevent

__author__ = 'jason'


class RequestorService(BaseService):
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
            gevent.idle()
