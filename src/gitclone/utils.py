import sys

from functools import wraps

from rich import print


def rpartition(s, d):
    res = s.rpartition(d)
    if res[0]:
        return (res[0], res[2])
    return (res[2], res[0])
