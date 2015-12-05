# Lib
from v2.system.canned_os import CannedOS
from v2.services.analyzer import AnalyzerService
from v2.services.initializer import InitializerService
from v2.services.requestor import RequestorService
from v2.services.db import DBService
from v2.services.queue import QueueService
from v2.data.db import MemDB
from v2.data.queue import MemQueue
from v2.data.timings import ResourceTimings, Resource

# Ext
import gevent

# Global Cache
# CacheControl will use DictCache by default


__author__ = 'jason'


def github_events_resource():
    token = 'c0698ac78b8f29412f9a358bacd2d34711cdf217'
    headers = {
        'User-Agent': 'CodeStats-Machine',
        'Authorization': "token %s" % token
    }

    timings = ResourceTimings()
    resource = Resource("https://api.github.com/events", timings, send_headers=headers)

    return resource


def main():
    """
    Main
    :return:
    """

    # needed objects
    os = CannedOS("CannedOS")
    # mem_db = MemDB()
    # mem_queue = MemQueue()
    #
    # # add entries to mem queue
    # mem_db.save_resource(github_events_resource())

    # create initializer
    # initializer = InitializerService("initializer-service")
    # initializer.db = mem_db
    # initializer.queue = mem_queue

    # create analyzer and continue setup
    # analyzer = AnalyzerService("analyzer-service")
    # analyzer.db = mem_db
    # analyzer.queue = mem_queue

    os.bootup()

    os.schedule_service(DBService, "database-service", True)
    os.schedule_service(QueueService, "queue-service", True)
    os.schedule_service(AnalyzerService, "analyzer-service", True)
    os.schedule_service(InitializerService, "initializer-service", True)
    os.schedule_service(RequestorService, "requestor-service", True)
    # os.schedule_provided_service(analyzer)
    # os.schedule_provided_service(initializer)

    def stop():
        os.shutdown()

    stop_event = gevent.spawn_later(5, stop)
    gevent.joinall([os.start(), stop_event])

main()
