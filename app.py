# Lib
from v2.system.canned_os import CannedOS
from v2.services.analyzer import AnalyzerService
from v2.services.initializer import InitializerService
from v2.services.requestor import RequestorService
from v2.services.response import ResponseParserService
from v2.services.db import DBService
from v2.services.queue import QueueService
from v2.data.timings import ResourceTimings, Resource

# Ext
import gevent

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

    os = CannedOS("CannedOS")
    os.bootup()

    # == support services ==
    os.schedule_service(DBService, "database-service", True)
    os.schedule_service(QueueService, "queue-service", True)

    # == action services ==

    # reads either file or db and prims the queue - right now hard coded
    os.schedule_service(InitializerService, "initializer-service", True)

    # analyzer pulls from queue things to analyze, if a resource can
    # be requested it is sent to the requestor queue to be requested
    os.schedule_service(AnalyzerService, "analyzer-service", True)

    # requestor pulls from the request queue and executes a request
    # the response is then put on the publish queue
    os.schedule_service(RequestorService, "requestor-service", True)

    # response service will read from the publish queue and
    # parse the response, updating the timings and doing other
    # data intense tasks. One complete the resource is once again put
    # on the analyze queue
    os.schedule_service(ResponseParserService, "response-service", True)

    def stop_os():
        os.shutdown()

    def stop():
        return gevent.spawn_later(120, stop_os)

    gevent.joinall([stop()])

main()
