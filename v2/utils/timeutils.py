from time import time

__author__ = 'jason'


def milliseconds():
    return int(round(time() * 1000))  # round is safer than floor which int does natively


def seconds():
    return int(round(time()))

# def seconds_str_to_milliseconds_str(seconds_str):
    # convert seconds string to seconds
    # convert seconds to milliseconds
    # convert milliseconds to str
    # seconds_str
