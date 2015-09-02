# External
import requests
import requests_mock
import json
import time

# Lib
from system.os import Scheduler
from system.states import BaseStates


def test_scheduler():
    scheduler = Scheduler("scheduler")
    assert scheduler.service_state == BaseStates.Idle

    scheduler.start()
    assert scheduler.service_state == BaseStates.Started

    scheduler.stop()
    assert scheduler.service_state == BaseStates.Stopped
