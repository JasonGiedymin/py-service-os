# External
import requests
import requests_mock
import json
import time

# Lib
from data.engine import GHRequestEngine, States


def register_mock_testdata(adapter):

    adapter.register_uri('GET', 'mock://event-test', [
        {'text': 'data1', 'status_code': 200},
        {'text': 'data2', 'status_code': 200, 'headers': {'x': 'x'}}
    ])

    return adapter


def register_mock_github_events(adapter):
    data_file = open('./tests/system/mock_data/get_event_body.json', 'r')
    data = json.load(data_file)

    adapter.register_uri('GET', 'mock://github/events', [
        {
            'text': json.dumps(data),
            'status_code': 200,
            'headers': {
                'X-RateLimit-Limit': '5000',
                'X-RateLimit-Remaining': '4994',
                'X-RateLimit-Reset': '1440648111',
                'X-Poll-Interval': '2',
                'Cache-Control': 'private, max-age=60, s-maxage=60',
                'Last-Modified': 'Wed, 26 Aug 2015 20:13:37 GMT',
                'ETag': '1fa058896df286d636d0f75c69556f03'

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
    Factory
    :return:
    """
    session = requests.Session()
    adapter = create_adapter()
    session.mount('mock', adapter)

    return GHRequestEngine(session)


def create_mock():
    """
    Factory
    :return:
    """
    return requests_mock.mock()
