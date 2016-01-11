from enum import Enum


__author__ = 'jason'


class BaseStates(Enum):
    Started = 0   # service started
    Stopped = 1   # service stopped
    Idle = 2      # service idle, just created
    Starting = 3  # service is the middle of starting
    Stopping = 4  # service is in the middle of stopping


class EventLoopStates(Enum):
    Tick = 0
    Tock = 1
