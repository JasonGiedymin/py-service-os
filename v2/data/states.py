from enum import Enum


__author__ = 'jason'


class ResourceStates(Enum):
    Idle = 0  # not really used anymore
    Error = 1
    WaitingForInterval = 2
    WaitingForReset = 3
    HasOwner = 4  # resource is already claimed
    EdgeError = 5  # edge case error
