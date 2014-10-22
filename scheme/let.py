from scheme.environment import Environment
from scheme.procedure import SimpleProcedure


__author__ = 'perkins'

from scheme.macro import Macro, MacroSymbol
from scheme.Globals import Globals
from zope.interface import implements


class let(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        env = processer.cenv
        if isinstance(params[0], list):
            bindings = params[0]
            for binding in bindings:
                if len(binding[1:])!=1:
                    raise SyntaxError("let requires a list of pairs for its first argument")
                env[binding[0]]=processer.process([binding[1]], Environment(env))
            processer.process(params[1:], env)
            return
        name=params[0]
        bindings=params[1]
        vars = [i[0] for i in bindings]
        vals = [processer.process(i[1], Environment(env)) for i in bindings]
        proc = SimpleProcedure([vars]+params[2:], env).setName(name)
        env[name]=proc
        LOG(32, [proc]+vals)
        ret = processer.process([[proc]+vals])
        processer.popStack(ret)
        processer.stackPointer+=1
        return
        #{('lambda:%s' % t): SimpleProcedure([args] + rest, processer.cenv).setName("lambda:%s"%t)})





Globals['let'] = let()
