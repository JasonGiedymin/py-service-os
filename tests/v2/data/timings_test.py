from v2.data.timings import ResourceTimings
from v2.utils import timeutils

__author__ = 'jason'


def test_resource_timings():
    interval = 1000
    rate_limit = 1
    rate_limit_remaining = 1
    time_to_reset = 60
    etag = "ABCD"

    # default timings
    timings = ResourceTimings()

    # == assert defaults ==
    assert timings.interval == 1000
    assert timings.rate_limit == 1
    assert timings.rate_limit_remaining == 1
    assert timings.time_to_reset == 60
    assert timings.etag is None
    assert timings.last_request_timestamp is None

    # Update timestamp
    timings.update_timestamp()
    assert timings.last_request_timestamp is not None
    assert timings.last_request_timestamp > 0

    timings = ResourceTimings(interval, rate_limit, rate_limit_remaining,
                              time_to_reset, etag)

    # == asserts assignments ==
    assert timings.interval == interval
    assert timings.rate_limit == rate_limit
    assert timings.rate_limit_remaining == rate_limit_remaining
    assert timings.time_to_reset == time_to_reset
    assert timings.etag == etag

    # == assert methods ==
    old_timestamp = timings.last_request_timestamp
    timings.update_timestamp()
    assert timings.last_request_timestamp is not None
    assert timings.last_request_timestamp > old_timestamp


def test_timings_limit_reached():
    timings = ResourceTimings()  # default timings
    timings.rate_limit_remaining = 0
    assert timings.has_limit_been_reached()


def test_timings_reset_window():
    timings = ResourceTimings()  # default timings

    timings.time_to_reset = timeutils.milliseconds() + 1000  # one second or 1000 ms from now
    assert not timings.has_reset_window_past()

    timings.time_to_reset = timeutils.milliseconds() - 1000  # one second or 1000 ms ago
    assert timings.has_reset_window_past()


def test_timings_requested_since_reset_window():
    timings = ResourceTimings()  # default timings

    timings.time_to_reset = timeutils.milliseconds() - 1000  # past
    timings.last_request_timestamp = timeutils.milliseconds() + 1000  # was done after reset
    assert timings.requested_since_reset()


def test_timings_interval_past():
    timings = ResourceTimings()  # default timings

    # Update timestamp to 2000ms ago
    timings.last_request_timestamp = timeutils.milliseconds() - 2000

    # test that interval has not passed if set to 10000ms
    timings.interval = 10000
    timings.update_interval_timestamp()
    assert timings.has_interval_passed() is False

    # set interval to 1000, which when added to the timestamp should be less than now
    timings.interval = 1000
    timings.update_interval_timestamp()
    assert timings.has_interval_passed() is True

    # set the interval timestamp to now, this test can only be passed if the
    # interval PAST now, not equal
    now = timings.get_now()
    timings.interval_timestamp = now
    assert timings.has_interval_passed(now) is False

    # since the resolution is in milliseconds, one milliseconds is enough to ensure
    # the interval is passed
    timings.interval_timestamp = now - 1  # making it minus 1ms will make it past
    assert timings.has_interval_passed(now) is True
