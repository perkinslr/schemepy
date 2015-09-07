__author__ = 'perkins'

from zope.interface import implements

from scheme.macro import Macro, MacroSymbol
from scheme.procedure import SimpleProcedure
from processer import Globals
import time
import scheme
from scheme import jit

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
        proc = SimpleProcedure([args] + rest, processer.cenv).setName("lambda:%s" % t)
        if jit.enabled and jit.lambdas_enabled:
            proc = jit.makeFunction(proc)
        ret = MacroSymbol('lambda:%s' % t).setEnv(
            {('lambda:%s' % t): proc})
#        lambdas.append(ret)
        return ret


Globals.Globals['lambda'] = Lambda()
