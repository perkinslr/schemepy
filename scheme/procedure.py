from zope import interface


# noinspection PyUnusedLocal
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
        self.name = None
    def __call__(self, processer, args):
        retval = None
        env = Environment(self.env)
        if (isinstance(self.ast[0], list)):
            if '.' in self.ast[0]:
                iter_args = iter(args)
                for idx, item in enumerate(self.ast[0][:-2]):
                    i = iter_args.next()
                    env[item] = i
                env[self.ast[0][-1]] = list(iter_args)
            else:
                if (len(args) != len(self.ast[0])):
                    raise TypeError("%r expected exactly %i arguments, got %i" % (self, len(self.ast[0]), len(args)))
                for idx, item in enumerate(self.ast[0]):
                    i = args[idx]
                    env[item] = i
        else:
            env[self.ast[0]] = args
        for i in self.ast[1:]:
            c = deepcopy([i])
            processer.pushStack(c)
            icd = processer.callDepth
            retval = processer.doProcess(c, env)
            while icd < processer.callDepth:
                processer.popStackN()
            processer.popStack(retval)
        if (isinstance(retval, Symbol)) and retval.isBound(env):
            return retval.toObject(env)
        return retval
    def setName(self, name):
        self.name = name
        return self
    def __repr__(self):
        if self.name:
            return '<SimpleProcedure %s>' % self.name
        return object.__repr__(self)
