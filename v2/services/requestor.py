import requests
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
    Requests resources.
    """
    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        BaseService.__init__(self, name, parent_logger=parent_logger, enable_service_recovery=enable_service_recovery)
        self.queue = None

    def set_queue(self, queue):
        self.queue = queue

    def register(self):
        self.queue = self.get_directory_service_proxy().get_service("queue-service")

    def event_loop(self):
        """
        The event loop.
        """
        while self.should_loop():
            resource = self.queue.get_requests()  # pop from queue

            if resource is not None:  # if an item exists
                self.log.debug("found resource to request")

                session = requests.Session()
                session.headers = resource.send_headers
                session.headers.update({
                    "If-None-Match": '%s' % resource.timings.etag
                })

                resp = session.get("https://api.github.com/events")
                self.log.info("request complete", status_code=resp.status_code, resource_id=str(resource.id))
                # self.log.info(resp.headers)
                # self.log.info(resp.content)

                # put Tuple(Resource, Response) in publish queue
                self.queue.put_publish((resource, resp))
                self.log.debug("resource put on publish queue for parsing, size: [%d]" % self.queue.publish_size())

            gevent.sleep(2)
            gevent.idle()
