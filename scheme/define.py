from zope.interface import implements

from scheme.macro import Macro, SimpleMacro
from scheme.procedure import SimpleProcedure
from processer import Globals
from scheme.symbol import Symbol

class define(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        if not isinstance(params[0], list):
            env = processer.cenv.parent
            name = params[0]
            value = processer.process(params[1:], env)
            env[name] = value
        else:
            name = params[0][0]
            args = params[0][1:]
            rest = params[1:]
            env = processer.cenv.parent if processer.cenv is not Globals.Globals else Globals.Globals
            if isinstance(name, list):
                from scheme.Lambda import Lambda
                l=Lambda()
                x = name
                o=[]
                while isinstance(x, list):
                    o.append(x)
                    x=x[0]
                name=x
                retval = []
                retval.append(Symbol('define'))

                retval.append(o[-1])
                retval.append([Symbol('lambda'), args, [Symbol('begin')] + rest])
                processer.process(retval, env)
            else:
                env[name] = SimpleProcedure([args] + rest, env).setName(name)
        processer.popStack(None)
        #processer.ast[processer.stackPointer]=None
        processer.stackPointer+=1
        return None


class Set(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        env = processer.cenv.parent
        if not isinstance(params[0], list):
            name = params[0]
            value = processer.process(params[1:], env)
            if not name.isBound(env):
                raise NameError("Name %s unbound in enclosing namespaces" % name)
            name.getEnv(env)[name] = value
        else:
            name = params[0][0]
            args = params[0][1:]
            rest = params[1:]
            if not name.isBound(env):
                raise NameError("Name %s unbound in enclosing namespaces" % name)
            name.getEnv(env)[name] = SimpleProcedure([args] + rest, processer.cenv.parent).setName(name)
        #processer.ast[processer.stackPointer]=None
        processer.popStack(None)
        processer.stackPointer+=1
        return None


class defmacro(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        if len(params) == 2 and not isinstance(params[0], list) and ((isinstance(params[1], list) and params[1][0]=='lambda') or not (isinstance(params[1], list))):
            name = params[0]
            env = processer.cenv.parent if processer.cenv is not Globals.Globals else Globals.Globals
            proc = processer.process([params[1]], env)
            env[name] = SimpleMacro.wrappedMacro(proc, env)

        else:
            name = params[0][0]
            args = params[0][1:]
            rest = params[1:]
            env = processer.cenv.parent if processer.cenv is not Globals.Globals else Globals.Globals
            env[name] = SimpleMacro([args] + rest, env).setName(name)
        #processer.ast[processer.stackPointer]=None
        processer.popStack(None)
        processer.stackPointer+=1
        return None


Globals.Globals['define'] = define()
Globals.Globals['set!'] = Set()
Globals.Globals['define-macro'] = Globals.Globals['defmacro'] = defmacro()
