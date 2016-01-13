# External
import requests
import requests_mock
import json
import time

# Lib
from data.engine import GHRequestEngine
from services.request import RequestMachine
from v2.utils import timeutils

GLOBAL_MOCK_REQUEST_INTERVAL = '2'
GLOBAL_MOCK_REQUEST_RATELIMIT = '5000'
GLOBAL_MOCK_REQUEST_REMAINING = '4994'
# GLOBAL_MOCK_REQUEST_RESET = '1440648111'
# GLOBAL_MOCK_REQUEST_RESET2 = '1440649111'
GLOBAL_MOCK_REQUEST_RESET = str(timeutils.seconds())  # here we stick with time as seconds
GLOBAL_MOCK_REQUEST_RESET2 = str(timeutils.seconds() + 1)
GLOBAL_MOCK_REQUEST_ETAG1 = '1fa058896df286d636d0f75c69556f03'


def register_mock_testdata(adapter):

    adapter.register_uri('GET', 'mock://event-test', [
        {'text': 'data1', 'status_code': 200},
        {'text': 'data2', 'status_code': 200, 'headers': {'x': 'x'}}
    ])

    return adapter


def register_mock_github_quickinterval_events(adapter):
    """
    Generates a sequence of quick interval responses good for
    testing the analyzer and freeze services.
    :param adapter:
    :return:
    """

    data_file = open('./tests/system/mock_data/get_event_body.json', 'r')
    data = json.load(data_file)
    common_request = {
        'text': json.dumps(data),
        'status_code': 200,
        'headers': {
            'X-RateLimit-Limit': GLOBAL_MOCK_REQUEST_RATELIMIT,
            'X-RateLimit-Remaining': GLOBAL_MOCK_REQUEST_REMAINING,
            'X-RateLimit-Reset': str(timeutils.seconds() + 60),
            'X-Poll-Interval': '1',
            'Cache-Control': 'private, max-age=60, s-maxage=60',
            'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
            'ETag': GLOBAL_MOCK_REQUEST_ETAG1

        }
    }

    def times():
        data = []

        for n in range(100):
            common_request['headers']['mock-sequence-id'] = "%d" % n
            data.append(common_request)

        return data

    adapter.register_uri('GET', 'mock://github/events-quick-interval', times())
    return adapter


def register_mock_github_events(adapter):
    data_file = open('./tests/system/mock_data/get_event_body.json', 'r')
    data = json.load(data_file)

    adapter.register_uri('GET', 'mock://github/events', [
        {
            'text': json.dumps(data),
            'status_code': 200,
            'headers': {
                'X-RateLimit-Limit': GLOBAL_MOCK_REQUEST_RATELIMIT,
                'X-RateLimit-Remaining': GLOBAL_MOCK_REQUEST_REMAINING,
                'X-RateLimit-Reset': GLOBAL_MOCK_REQUEST_RESET,
                'X-Poll-Interval': GLOBAL_MOCK_REQUEST_INTERVAL,
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': GLOBAL_MOCK_REQUEST_ETAG1
            }
        }
    ])

    adapter.register_uri('GET', 'mock://github/events/withetag', [
        {
            'text': json.dumps(data),
            'status_code': 304,
            'headers': {
                'X-RateLimit-Limit': GLOBAL_MOCK_REQUEST_RATELIMIT,
                'X-RateLimit-Remaining': GLOBAL_MOCK_REQUEST_REMAINING,
                'X-RateLimit-Reset': GLOBAL_MOCK_REQUEST_RESET,
                'X-Poll-Interval': GLOBAL_MOCK_REQUEST_INTERVAL + '0',  # will be '20'
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': GLOBAL_MOCK_REQUEST_ETAG1
            }
        }
    ])

    adapter.register_uri('GET', 'mock://github/events/limits', [
        {
            'text': json.dumps(data),
            'status_code': 200,
            'headers': {
                'X-RateLimit-Limit': '1',
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(time.time()),
                'X-Poll-Interval': '1',
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': GLOBAL_MOCK_REQUEST_ETAG1
            }
        },
        {
            'text': json.dumps(data),
            'status_code': 200,
            'headers': {
                'X-RateLimit-Limit': '1',
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(time.time()),
                'X-Poll-Interval': '1',
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': GLOBAL_MOCK_REQUEST_ETAG1
            }
        }
    ])

    adapter.register_uri('GET', 'mock://github/events/statustest', [
        {
            'text': json.dumps(data),
            'status_code': 200,
            'headers': {
                'X-RateLimit-Limit': GLOBAL_MOCK_REQUEST_RATELIMIT,
                'X-RateLimit-Remaining': GLOBAL_MOCK_REQUEST_REMAINING,
                'X-RateLimit-Reset': GLOBAL_MOCK_REQUEST_RESET,
                'X-Poll-Interval': GLOBAL_MOCK_REQUEST_INTERVAL,
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': GLOBAL_MOCK_REQUEST_ETAG1
            }
        },
        {
            'text': json.dumps(data),
            'status_code': 304,
            'headers': {
                'X-RateLimit-Limit': GLOBAL_MOCK_REQUEST_RATELIMIT,
                'X-RateLimit-Remaining': GLOBAL_MOCK_REQUEST_REMAINING,
                'X-RateLimit-Reset': GLOBAL_MOCK_REQUEST_RESET,
                'X-Poll-Interval': GLOBAL_MOCK_REQUEST_INTERVAL,
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': GLOBAL_MOCK_REQUEST_ETAG1
            }
        },
        {
            'text': json.dumps(data),
            'status_code': 403,
            'headers': {
                'X-RateLimit-Limit': GLOBAL_MOCK_REQUEST_RATELIMIT,
                'X-RateLimit-Remaining': GLOBAL_MOCK_REQUEST_REMAINING,
                'X-RateLimit-Reset': GLOBAL_MOCK_REQUEST_RESET,
                'X-Poll-Interval': GLOBAL_MOCK_REQUEST_INTERVAL,
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': GLOBAL_MOCK_REQUEST_ETAG1
            }
        },
        {
            'text': json.dumps(data),
            'status_code': 404,
            'headers': {
                'X-RateLimit-Limit': GLOBAL_MOCK_REQUEST_RATELIMIT,
                'X-RateLimit-Remaining': GLOBAL_MOCK_REQUEST_REMAINING,
                'X-RateLimit-Reset': GLOBAL_MOCK_REQUEST_RESET,
                'X-Poll-Interval': GLOBAL_MOCK_REQUEST_INTERVAL,
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': GLOBAL_MOCK_REQUEST_ETAG1
            }
        },
        {
            'text': json.dumps(data),
            'status_code': 500,
            'headers': {
                'X-RateLimit-Limit': GLOBAL_MOCK_REQUEST_RATELIMIT,
                'X-RateLimit-Remaining': GLOBAL_MOCK_REQUEST_REMAINING,
                'X-RateLimit-Reset': GLOBAL_MOCK_REQUEST_RESET,
                'X-Poll-Interval': GLOBAL_MOCK_REQUEST_INTERVAL,
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': GLOBAL_MOCK_REQUEST_ETAG1
            }
        }
    ])

    adapter.register_uri('GET', 'mock://somedomain/withoutheaders', [
        {
            'text': json.dumps(data),
            'status_code': 200,
            'headers': {
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': GLOBAL_MOCK_REQUEST_ETAG1
            }
        }
    ])

    return adapter


def register_mock_endpoints(adapter):
    """
    Registers any mock endpoints used.
    :param adapter:
    :return:
    """

    register_mock_testdata(adapter)
    register_mock_github_events(adapter)
    register_mock_github_quickinterval_events(adapter)

    return adapter


def create_adapter():
    """
    Factory
    :return:
    """
    adapter = requests_mock.Adapter()
    return register_mock_endpoints(adapter)


def create_mock_engine():
    """
    Deprecated
    Factory
    :return:
    """
    session = requests.Session()
    adapter = create_adapter()
    session.mount('mock', adapter)

    return GHRequestEngine(session)


def create_mock_session():
    session = requests.Session()
    adapter = create_adapter()
    session.mount('mock', adapter)
    return session


def create_mock_request_machine(request_spec):
    session = create_mock_session()
    return RequestMachine(session, request_spec)


def create_mock():
    """
    Factory
    :return:
    """
    return requests_mock.mock()
