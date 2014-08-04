__author__ = 'jeanie'

from scheme.procedure import Procedure
from scheme.Globals import Globals
from zope.interface import implements


class begin(object):
    implements(Procedure)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        env = processer.cenv.parent
        ret = processer.process(params, env)
        return ret


Globals['begin'] = begin()