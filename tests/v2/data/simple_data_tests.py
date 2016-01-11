from v2.data.simple_data import ServiceMetaData


def test_retry_limit():
    s1 = ServiceMetaData("s1",delay=0,retries=1,recovery_enabled=False)
    # s2 = ServiceMetaData("s2",delay=0,retries=5,recovery_enabled=False)
    # s3 = ServiceMetaData("s3",delay=0,retries=10,recovery_enabled=False)

    # == just started
    s1.starts = 1
    assert s1.retry_limit_reached() is False

    # == first start + 1 retry = 2 starts
    s1.starts = 2
    assert s1.retry_limit_reached() is True

    # == normal increment
    s1.retries = 10
    s1.starts = 10
    assert s1.retry_limit_reached() is False

    s1.starts = 11
    assert s1.retry_limit_reached() is True

    # == abnormal usage - initial creation
    s1.retries = 0
    s1.starts = 0
    assert s1.retry_limit_reached() is False

    s1.starts = 1
    assert s1.retry_limit_reached() is True

    # == abnormal usage - infinite retries
    s1.retries = -1
    s1.starts = 0
    assert s1.retry_limit_reached() is False

    s1.starts = 1
    assert s1.retry_limit_reached() is False

    s1.starts = 2
    assert s1.retry_limit_reached() is False

    s1.starts = 3
    assert s1.retry_limit_reached() is False
