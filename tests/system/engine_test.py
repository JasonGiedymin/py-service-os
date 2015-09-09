__author__ = 'jason'


# External
import json
import time

# Lib
from data.engine import States

# Helpers
import mock_requests


def test_create():
    engine = mock_requests.create_mock_engine()

    assert engine is not None


def test_engine_states():
    engine = mock_requests.create_mock_engine()
    assert engine.get_state() == States.Idle
    engine._set_running()
    assert engine.get_state() == States.Running


def test_get_prep():
    """
    This tests that the factory and response list works as the
    test framework sets it up.
    :return:
    """
    engine = mock_requests.create_mock_engine()

    resp = engine.get('mock://event-test', 'test')
    assert resp is not None
    assert (resp.status_code, resp.text) == (200, 'data1')

    resp = engine.get('mock://event-test', 'test')
    assert resp is not None
    assert (resp.status_code, resp.text) == (200, 'data2')

    assert resp.headers['x'] == 'x'


def test_get_events():
    """
    This tests that the factory and response list works as the
    test framework sets it up.
    :return:
    """
    engine = mock_requests.create_mock_engine()

    resp = engine.get_events(url='mock://github/events')
    assert resp is not None
    assert resp.status_code == 200
    assert resp.headers['X-RateLimit-Limit'] == '5000'

    json_body = json.loads(resp.content)
    assert json_body is not None
    assert len(json_body) == 30


def test_engine_limits():
    engine = mock_requests.create_mock_engine()
    resp = engine.get_events(url='mock://github/events')

    assert engine.limits is not None
    assert 'events' in engine.limits

    curr_limits = engine.limits['events']

    assert curr_limits.last_op_time > 0 # we record the time get took place
    assert curr_limits.xrate_limit == '5000'
    assert curr_limits.xrate_limit_remaining == '4994'
    assert curr_limits.next_reset == '1440648111'
    assert curr_limits.xpoll_interval == '2'
    assert curr_limits.cache_control == 'private, max-age=60, s-maxage=60'
    assert curr_limits.last_modified == 'Wed, 26 Aug 2015 20:13:37 GMT'
    assert curr_limits.etag == '1fa058896df286d636d0f75c69556f03'


def test_poll_interval():
    """
    Test that the engine respects the poll interval.
    :return:
    """
    engine = mock_requests.create_mock_engine()

    # make first call
    t1 = time.time()
    resp1 = engine.get_events(url='mock://github/events')

    # make second call, respecting the test's specified interval
    resp2 = engine.get_events(url='mock://github/events')
    t2 = time.time()

    # test specified interval is 2 seconds t3 should be > than 2.
    t3 = t2 - t1
    assert t3 > 2


def test_engine_eventloop():
    engine = mock_requests.create_mock_engine()
    engine.start()
    engine.join()


def test_ratelimit_exceeded():
    pass


def test_ratelimit_exceeded_and_ttr():
    """
    ttr: time till reset
    """
    pass

