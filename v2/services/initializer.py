# Lib
from v2.system.services import BaseService
from v2.data.timings import ResourceTimings, Resource

# System
import gevent

__author__ = 'jason'


def github_events_resource():
    """
    Generate an initial event, in this case a github event.

    :return:
    """
    token = 'c0698ac78b8f29412f9a358bacd2d34711cdf217'
    headers = {
        'User-Agent': 'CodeStats-Machine',
        'Authorization': "token %s" % token
    }

    timings = ResourceTimings()
    resource = Resource("https://api.github.com/events", timings, send_headers=headers)

    return resource


class InitializerService(BaseService):
    """
    Put resources into a queue.
    """
    def __init__(self, name, parent_logger=None, enable_service_recovery=False):
        BaseService.__init__(self, name, parent_logger=parent_logger, enable_service_recovery=enable_service_recovery)
        self.current_batch = []
        self.db = None
        self.queue = None
        self.registered = {}  # simple dict cache keeping resources already registered

    def seed_data(self):
        self.db.save_resource(github_events_resource())
        self.log.debug("data seeded, entry count: [%d]." % self.db.resource_count())

    def register(self):
        self.db = self.get_directory_service_proxy().get_service("database-service")
        self.queue = self.get_directory_service_proxy().get_service("queue-service")
        self.seed_data()

    def event_loop(self):
        """
        The event loop.
        Resource reloading is disabled at the moment.
        """
        while self.should_loop():
            for res_uri, res in self.db.get_resources():
                if res_uri not in self.registered:
                    self.queue.put_analyze(res)
                    self.registered[res_uri] = res
                    self.log.info("registered new resource, id:[%s], uri:[%s], size: [%d]" % (res.id, res_uri, self.queue.analyze_size()))
                # else:  # resource already exists
                    # if resource.reload:  # check if it needs reloading
                    #     self.registered.pop(resource.id)  # popping it will reload it next loop
                    #     self.log.debug("resource set to be reloaded, id:[%s], uri:[%s]" % (resource.id, resource.uri))

            gevent.idle()
