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
        print 18, env
        if isinstance(params[0], list):
            bindings = params[0]
            e=Environment(env)
            for binding in bindings:
                print 223, binding
                if len(binding[1:])!=1:
                    raise SyntaxError("let requires a list of pairs for its first argument")
                if isinstance(binding[1], list):
                    b = binding[1]
                else:
                    b=[binding[1]]

                processer.pushStackN()
                print 330, b, binding[1]
                r = processer.process(b, Environment(env), processer.initialCallDepth+100)
                print 332, r
                processer.popStackN()


                e[binding[0]]= r
            print 399, params, processer.ast
            r = processer.process(params[1:], e, processer.callDepth)
            processer.popStack(r)
            print 411, r, processer.ast, processer.callDepth, processer.callStack.queue
            #processer.stackPointer+=1
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
