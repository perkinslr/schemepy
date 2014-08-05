from zope import interface


# noinspection PyUnusedLocal
from scheme import debug
from scheme.environment import Environment
from scheme.symbol import Symbol
from scheme.utils import deepcopy


# noinspection PyMethodParameters,PyUnusedLocal
class Procedure(interface.Interface):
    def __init__(ast, env):
        """"""

    def __call__(processer, params):
        """"""


class SimpleProcedure(object):
    interface.implements(Procedure)
    def __init__(self, ast, env):
        self.ast = ast
        self.env = env
        self.name=None
    def __call__(self, processer, args):
        retval = None
        env = Environment(self.env)
        if (isinstance(self.ast[0], list)):
            if '.' in self.ast[0]:
                idx = 0
                for idx, item in enumerate(self.ast[0][:-2]):
                    i = args[idx]
                    env[item] = i
                env[self.ast[0][-1]] = args[idx+1:]
            else:
                if (len(args) != len(self.ast[0])):
                    raise TypeError("%r expected exactly %i arguments, got %i" %(self, len(self.ast[0]), len(args)))
                for idx, item in enumerate(self.ast[0]):
                    i = args[idx]
                    env[item] = i
        else:
            env[self.ast[0]] = args
        if debug.DEBUG:
            print env
        for i in self.ast[1:]:
            retval = processer.process(deepcopy([i]), env)
        if (isinstance(retval, Symbol)):
            return retval.toObject(env)
        return retval
    def setName(self, name):
        self.name=name
        return self
    def __repr__(self):
        if self.name:
            return '<SimpleProcedure %s>'%self.name
        return object.__repr__(self)