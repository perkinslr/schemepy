__author__ = 'perkins'

from zope.interface import implements

from scheme.macro import Macro, MacroSymbol
from scheme.procedure import SimpleProcedure
from processer import Globals
import time
import scheme


lambdas = []


class Lambda(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, *a):

        if len(a) == 1:
            processer = scheme.processer.processer
            params = a[0]
        else:
            processer, params = a
        args = params[0]
        rest = params[1:]

        t = repr(time.time())

        ret = MacroSymbol('lambda:%s' % t).setEnv(
            {('lambda:%s' % t): SimpleProcedure([args] + rest, processer.cenv).setName("lambda:%s" % t)})
        lambdas.append(ret)
        return ret


Globals.Globals['lambda'] = Lambda()