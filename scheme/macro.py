from zope.interface import providedBy
from scheme.environment import Environment
from scheme.procedure import Procedure
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
    @classmethod
    def wrappedMacro(cls, proc, env):
        while (isinstance(proc, Symbol)):
            proc=proc.toObject(env)
        pb = providedBy(proc)
        if Macro in pb:
            return proc
        if Procedure in pb:
            return cls(None,env,proc).setName(proc.name)
        #    return cls(proc.ast, proc.env).setName(proc.name)
        return cls(None,env,proc)
    def __init__(self, ast, env,wrapped=None):
        self.ast = ast
        self.env = env
        self.name=None
        self.wrapped=wrapped
    # noinspection PyUnusedLocal
    def __call__(self, processer, args):
        if self.wrapped:
            if Procedure in providedBy(self.wrapped):
                return self.wrapped(processer, args)
            return self.wrapped(args)
        retval = None
        env = Environment(self.env)
        if (isinstance(self.ast[0], list)):
            #if len(self.ast[0])==1:
            #    print 42
            #    env[self.ast[0][0]] = [Symbol('quote'), args]
            if '.' in self.ast[0]:
                idx = 0
                item = None
                for idx, item in enumerate(self.ast[0][:-2]):
                    i = args[idx]
                    env[item] = i
                env[self.ast[0][-1]] = [Symbol('quote'), args[idx:]]
            else:
                if len(self.ast[0]) != len(args):
                    raise SyntaxError("Macro %r requires exactly %i args, %i given" % (self, len(self.ast[0]), len(args)))
                for idx, item in enumerate(self.ast[0]):
                    i = args[idx]
                    env[item] = i
        else:
            env[self.ast[0]] = [Symbol('quote'), args]
        retval = copy_with_replacement(self.ast[1:], **env)
        retval = processer.process(retval, processer.cenv)
        processer.popStack(retval)
        return
    def setName(self, name):
        self.name=name
        return self
    def __repr__(self):
        if self.name:
            return '<SimpleMacro %s>'%self.name
        return object.__repr__(self)