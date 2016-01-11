# Lib
from v2.data.processors.response_parser import ResponseParser
from v2.services.services import BaseService

# System
import gevent

__author__ = 'jason'


class ResponseParserService(BaseService):
    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        BaseService.__init__(self, name, parent_logger=parent_logger, enable_service_recovery=enable_service_recovery)
        self.response_parser = ResponseParser("response-parser", parent_logger=self.log)
        self.db = None
        self.queue = None

    def set_queue(self, queue):
        self.queue = queue

    def register(self):
        self.db = self.get_directory_service_proxy().get_service("database-service")
        self.queue = self.get_directory_service_proxy().get_service("queue-service")

    def event_loop(self):
        """
        The event loop.
        """
        while self.should_loop():
            resource, response = self.queue.get_publish()  # pop from queue

            if resource is not None and response is not None:  # if an item exists
                self.log.debug("found resource, parsing...")
                parse_success = self.response_parser.parse(response, resource)
                if parse_success:
                    self.queue.put_analyze(resource)
                    self.log.debug("resource id:[%s] parsed, and put on analyze queue for analysis, size: [%d]" %
                                   (str(resource.id), self.queue.analyze_size()))
            else:  # serious error if we got here
                # log the error and put on the publish error queue
                error_msg = "Found either resource or response that was None, resource: [%s], response: [%s]"
                self.log.error(error_msg % (resource, response))
                self.queue.put_publish_error((resource, response))
                self.log.error("resource put on publish error queue, size: [%d]" %
                               self.queue.get_publish_error())

            gevent.sleep(2)
            gevent.idle()
