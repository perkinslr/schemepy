__author__ = 'jeanie'

from scheme.macro import Macro
from scheme.Globals import Globals
from zope.interface import implements


class cond(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        env = processer.cenv
        for pair in params:
            if pair[0] == "else":
                return pair[1]
            if isinstance(pair[0], list):
                if processer.process([pair[0]], env):
                    return pair[1]
                continue
            else:
                if pair[0].toObject(env):
                    return pair[1]


Globals['cond'] = cond()