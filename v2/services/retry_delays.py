import math

__author__ = 'jason'


def no_delay(x):
    return 0


def basic_delay(x):
    """
    A basic delay following a very basic exponential curve.
    :param x:
    :return:
    """
    return math.ceil(math.pow(x, 1.5))
