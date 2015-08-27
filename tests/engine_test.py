__author__ = 'jason'


# External
import requests
import requests_mock
# import codecs
import json

# Lib
from data.engine import GHRequestEngine


def register_mock_testdata(adapter):

    adapter.register_uri('GET', 'mock://event-test', [
        {'text': 'data1', 'status_code': 200},
        {'text': 'data2', 'status_code': 200, 'headers': {'x': 'x'}}
    ])

    return adapter


def register_mock_github_events(adapter):
    data_file = open('./tests/mock_data/get_event_body.json', 'r')
    data = json.load(data_file)

    adapter.register_uri('GET', 'mock://github/events', [
        {
            'text': json.dumps(data),
            'status_code': 200,
            'headers': {
                'X-RateLimit-Limit': '5000',
                'X-RateLimit-Remaining': '4994',
                'X-RateLimit-Reset': '1440648111',
                'X-Poll-Interval': '60',
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


def test_create():
    engine = create_mock_engine()

    assert engine is not None


def test_get_prep():
    """
    This tests that the factory and response list works as the
    test framework sets it up.
    :return:
    """
    engine = create_mock_engine()

    resp = engine.get('mock://event-test')
    assert resp is not None
    assert (resp.status_code, resp.text) == (200, 'data1')

    resp = engine.get('mock://event-test')
    assert resp is not None
    assert (resp.status_code, resp.text) == (200, 'data2')

    assert resp.headers['x'] == 'x'


def test_get_events():
    """
    This tests that the factory and response list works as the
    test framework sets it up.
    :return:
    """
    engine = create_mock_engine()

    resp = engine.get('mock://github/events')
    assert resp is not None
    assert resp.status_code == 200
    assert resp.headers['X-RateLimit-Limit'] == '5000'

    json_body = json.loads(resp.content)
    assert json_body is not None
    assert len(json_body) == 30


def test_engine_limits():
    engine = create_mock_engine()
    resp = engine.get('mock://github/events')

    assert engine.limit is not None
    assert engine.limit.xrate_limit == '5000'
    assert engine.limit.xrate_limit_remaining == '4994'
    assert engine.limit.next_reset == '1440648111'
    assert engine.limit.xpoll_interval == '60'
    assert engine.limit.cache_control == 'private, max-age=60, s-maxage=60'
    assert engine.limit.last_modified == 'Wed, 26 Aug 2015 20:13:37 GMT'
    assert engine.limit.etag == '1fa058896df286d636d0f75c69556f03'


def test_ratelimit_exceeded():
    pass


def test_ratelimit_exceeded_and_ttr():
    """
    ttr: time till reset
    """
    pass


def test_poll_interval():
    pass