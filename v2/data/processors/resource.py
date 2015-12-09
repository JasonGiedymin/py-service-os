from v2.data.states import ResourceStates
from v2.data.processors import DataProcessor

__author__ = 'jason'


class ResourceAnalyzer(DataProcessor):
    def __init__(self, name, parent_logger=None):
        DataProcessor.__init__(self, name, parent_logger)

    def is_edge_case(self, resource):
        value = resource.timings.has_limit_been_reached() \
               and resource.timings.has_reset_window_past() \
               and resource.timings.requested_since_reset()

        if value is True:
            self.log.error("resource has timings that exhibit an error edge case.",
                           resource_id=resource.id,
                           resource_uri=resource.uri)

        return value

    def can_request(self, resource):
        # == Base Checks == only check operationals at this point, for speed
        # checks if error exists
        if resource.has_error():
            self.log.error("resource is in state of error while trying to see if it can be requested.",
                           resource_id=resource.id,
                           resource_uri=resource.uri)
            return False, ResourceStates.Error

        # if someone owns the resource, it cannot be called. Think of it as a lock with semantics.
        if resource.has_owner():
            self.log.error("resource already has an owner registered to it.",
                           resource_owner=resource.owner,
                           resource_id=resource.id,
                           resource_uri=resource.uri)
            return False, ResourceStates.HasOwner

        # == Business Checks == now business logic can be accessed
        if self.is_edge_case(resource):
            self.log.error("resource was found to be in an edge case error state.",
                           resource_id=resource.id,
                           resource_uri=resource.uri)
            return False, ResourceStates.EdgeError

        # Kept here for ease of reading, but if performance is an issue, make instance or static methods
        def check_reset_window():
            if resource.timings.has_reset_window_past():
                self.log.debug("resource limit was reached, but can now be reset",
                               resource_id=resource.id,
                               resource_uri=resource.uri)
                return True
            else:
                self.log.debug("resource limit was reached, waiting for reset.",
                               limit=resource.timings.rate_limit_remaining,
                               resource_id=resource.id,
                               resource_uri=resource.uri)
                return False, ResourceStates.WaitingForReset

        def check_timings(next_fx):
            if resource.timings.has_limit_been_reached():
                return next_fx()
            else:
                msg = "resource interval passed, limit not yet exceeded, ready to be requested."
                self.log.debug(msg,
                               limit=resource.timings.rate_limit_remaining,
                               resource_id=resource.id,
                               resource_uri=resource.uri)
                return True

        def check_interval(next_fx):
            if resource.timings.has_interval_passed():
                return next_fx()
            else:
                self.log.debug("resource waiting for interval.",
                               resource_id=resource.id,
                               resource_uri=resource.uri)
                return False, ResourceStates.WaitingForInterval

        def then_check_timings(next_fx):
            return lambda: check_timings(next_fx)

        # would rather do pattern matching or a monadic map...
        return check_interval(then_check_timings(check_reset_window))
