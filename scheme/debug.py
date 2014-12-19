__author__ = 'perkins'

DEBUG = False


def LOG(*args):
    if not DEBUG:
        return
    for arg in args:
        print arg,
    print