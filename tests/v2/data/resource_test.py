from v2.data.timings import ResourceTimings, ResourceHeaders, Resource

__author__ = 'jason'


def test_resource_is_new():
    timings = ResourceTimings()  # default timings
    resource = Resource("mock://test", timings, ResourceHeaders())
    resource.owner = "TESTER"

    assert resource.is_new()

    # updating the timings with a timestamp will now signify that it is
    # not a new resource, that it has been used and a request has been
    # called.
    resource.timings.update_timestamp()
    assert resource.is_new() is False


def test_resource_has_owner():
    timings = ResourceTimings()  # default timings
    resource = Resource("mock://test", timings, ResourceHeaders())
    resource.owner = "TESTER"

    assert resource.has_owner()

