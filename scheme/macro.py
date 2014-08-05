from scheme.environment import Environment
from scheme.utils import copy_with_replacement


__author__ = 'perkins'

from zope import interface
from scheme.symbol import Symbol


# noinspection PyUnusedLocal,PyMethodParameters
class Macro(interface.Interface):
    def __init__(ast, env):
        """"""

    def __call__(processer, params):
        """"""


class MacroSymbol(Symbol):
    def toObject(self, env):
        return Symbol.toObject(self, self.env)
    def setEnv(self, env):
        # noinspection PyAttributeOutsideInit
        self.env = env
        return self


class SimpleMacro(object):
    interface.implements(Macro)
    def __init__(self, ast, env):
        self.ast = ast
        self.env = env
        self.name=None
    # noinspection PyUnusedLocal
    def __call__(self, processer, args):
        retval = None
        env = Environment(self.env)
        if (isinstance(self.ast[0], list)):
            if '.' in self.ast[0]:
                idx = 0
                item = None
                for idx, item in enumerate(self.ast[0][:-2]):
                    i = args[idx]
                    env[item] = i
                env[self.ast[0][-1]] = args[idx:]
            else:
                for idx, item in enumerate(self.ast[0]):
                    i = args[idx]
                    env[item] = i
        else:
            env[self.ast[0]] = args[0]
        retval = copy_with_replacement([Symbol('begin')] + self.ast[1:], **env)
        return retval
    def setName(self, name):
        self.name=name
        return self
    def __repr__(self):
        if self.name:
            return '<SimpleMacro %s>'%self.name
        return object.__repr__(self)