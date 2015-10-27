from v2.utils import timeutils
from v2.utils.loggers import Logger
from v2.data.states import ResourceStates

from uuid import uuid4
from enum import Enum


__author__ = 'jason'


class ResourceAnalyzer:
    def __init__(self, name):
        self.name = name
        self.log = Logger.get_logger(self.name)

    def is_edge_case(self, resource):
        value = resource.timings.has_limit_been_reached() \
               and resource.timings.has_reset_window_past() \
               and resource.timings.requested_since_reset()

        if value is True:
            self.log.error("resource [%s] has timings that exhibit an error edge case." % resource.unique_name)

        return value

    def can_request(self, resource):
        # == Base Checks == only check operationals at this point, for speed
        # checks if error exists
        if resource.has_error():
            self.log.error("resource [%s] is in state of error"
                           "while found trying to see if resource can be requested." % resource.__repr__())
            return False, ResourceStates.Error

        # if someone owns the resource, it cannot be called. Think of it as a lock with semantics.
        if resource.has_owner():
            self.log.error("resource [%s] already has an owner registered to it." % resource.__repr__())
            return False, ResourceStates.HasOwner

        # == Business Checks == now business logic can be accessed
        if self.is_edge_case(resource):
            self.log.error("resource [%s] was found to be in an edge case error state." % resource.__repr__())
            return False, ResourceStates.EdgeError

        # cyclomatic complexity is high here
        if resource.timings.has_interval_passed():
            if resource.timings.has_limit_been_reached():
                if resource.timings.has_reset_window_past():
                    self.log.debug("resource [%s] limit was reached, but can now be reset" % resource.__repr__())
                    return True
                else:
                    self.log.debug("resource [%s] limit was reached [%d], waiting for reset." %
                                   (resource.__repr__(), resource.timings.rate_limit_remaining))
                    return False, ResourceStates.WaitingForReset
            else:
                self.log.debug("resource [%s] interval passed, limit remaining: [%d], ready to be requested." % (resource.__repr__(), resource.timings.rate_limit_remaining))
                return True
        else:
            self.log.debug("resource [%s] waiting for interval." % resource.__repr__())
            return False, ResourceStates.WaitingForInterval

    # func (r *Resource) CanBeRequested() (bool, states.MachineState) {
    #     // if machine in error states stop
    #     if r.HasErrorState() {
    #         r.log.Debug("machine is in error state")
    #         return false, r.GetState()
    #     }
    #
    #     // if machine in abnormal states stop
    #     if r.IsBusy() {
    #         r.log.Debugf("machine is busy with state: %s", r.GetState())
    #         return false, r.GetState()
    #     }
    #
    #     // immediately check for edge case
    #     if r.IsEdgeCase() {
    #         r.log.Debug("edge case found")
    #         return false, states.ErrorEdgeCase
    #     }
    # ***** Here start work
    #     // ensure interval has past as requests cannot be made until that point
    #     if r.Timings.HasIntervalPast() {
    #         if !r.Timings.HasLimitBeenReached() {
    #             r.log.Debug("past interval, limit remaining, good to go")
    #             return true, states.Processing
    #         } else { // limit reached
    #             if r.Timings.HasResetWindowPast() {
    #                 r.log.Debug("past interval, limit reached, reset window past, good to go")
    #                 return true, states.Processing
    #             }
    #
    #             r.log.Debug("past interval, limit reached, waiting for reset")
    #             return false, states.WaitingForReset
    #         }
    #     }
    #
    #     r.log.Debug("waiting for interval to pass")
    #     return false, states.WaitingForInterval
    # }
