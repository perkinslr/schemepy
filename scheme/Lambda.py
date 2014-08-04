__author__ = 'perkins'

from zope.interface import implements

from scheme.macro import Macro, MacroSymbol
from scheme.procedure import SimpleProcedure
from processer import Globals
import time


class Lambda(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        args = params[0]
        rest = params[1:]
        t = repr(time.time())
        return MacroSymbol('lambda:%s' % t).setEnv(
            {('lambda:%s' % t): SimpleProcedure([args] + rest, processer.cenv.parent)})


Globals.Globals['lambda'] = Lambda()