from zope.interface import providedBy

from scheme.debug import LOG
from scheme.procedure import Procedure
from scheme.utils import copy_with_quasiquote, deepcopy


__author__ = 'perkins'

from zope import interface
from scheme.symbol import Symbol
from scheme.environment import Environment
import scheme


# noinspection PyUnusedLocal,PyMethodParameters
class Macro(interface.Interface):
    def __init__(ast, env):
        """"""

    def __call__(processer, params):
        """"""


class MacroSymbol(Symbol):
    def getEnv(self, env):
        if hasattr(self, 'env'):
            return self.env
        raise NameError("MacroSymbol has no associated environment")
    def setObj(self, obj):
        # noinspection PyAttributeOutsideInit
        self.obj = obj
        return self
    def toObject(self, env):
        # self.env.parent=env if env is not None else scheme.Globals.Globals
        if hasattr(self, 'obj'):
            return self.obj
        e = env
        while e is not None:
            if e is self.env:
                return Symbol.toObject(self, env)
            if hasattr(e, 'parent'):
                e = e.parent
            else:
                e = None
        return Symbol.toObject(self, self.env)
    def setEnv(self, env):
        # noinspection PyAttributeOutsideInit
        self.env = Environment(env)
        if not hasattr(self.env.parent, 'parent'):
            self.env.parent = Environment(scheme.Globals.Globals, env)
        # self.env.parent = env.parent if env is not None and hasattr(env, 'parent') else scheme.Globals.Globals
        return self


class SimpleMacro(object):
    interface.implements(Macro)
    @classmethod
    def wrappedMacro(cls, proc, env):
        while (isinstance(proc, Symbol)):
            proc = proc.toObject(env)
        pb = providedBy(proc)
        if Macro in pb:
            return proc
        if Procedure in pb:
            return cls(None, env, proc).setName(proc.name)
        # return cls(proc.ast, proc.env).setName(proc.name)
        return cls(None, env, proc)
    def __init__(self, ast, env, wrapped=None):
        self.ast = ast
        self.env = env
        self.name = None
        self.wrapped = wrapped
    # noinspection PyUnusedLocal
    def __call__(self, processer, args):
        if self.wrapped:
            if Procedure in providedBy(self.wrapped):
                return self.wrapped(processer, args)
            return self.wrapped(args)
        retval = None
        env = Environment(self.env)
        if (isinstance(self.ast[0], list)):
            # if len(self.ast[0])==1:
            # env[self.ast[0][0]] = [Symbol('quote'), args]
            if '.' in self.ast[0]:
                idx = -1
                item = None
                for idx, item in enumerate(self.ast[0][:-2]):
                    i = args[idx]
                    env[item] = i
                env[self.ast[0][-1]] = args[idx + 1:]
            else:
                if len(self.ast[0]) != len(args):
                    raise SyntaxError(
                        "Macro %r requires exactly %i args, %i given" % (self, len(self.ast[0]), len(args)))
                for idx, item in enumerate(self.ast[0]):
                    i = args[idx]
                    env[item] = i
        else:
            env[self.ast[0]] = [Symbol('quote'), args]
        o = []
        retval = copy_with_quasiquote(processer, env, deepcopy(self.ast[1:]), o_stack=o)[0]
        LOG("macro:79", retval)
        retval = processer.process(retval, processer.cenv)
        processer.popStack(retval)
        return
    def setName(self, name):
        self.name = name
        return self
    def __repr__(self):
        if self.name:
            return '<SimpleMacro %s>' % self.name
        return object.__repr__(self)
