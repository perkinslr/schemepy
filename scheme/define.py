from zope.interface import implements

from scheme.macro import Macro, SimpleMacro
from scheme.procedure import SimpleProcedure
from processer import Globals


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
            processer.cenv.parent[name] = SimpleProcedure([args] + rest, processer.cenv.parent)
        return [lambda *x: None]


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
            name.getEnv(env)[name] = SimpleProcedure([args] + rest, processer.cenv.parent)
        return [lambda *x: None]


class defmacro(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        name = params[0][0]
        args = params[0][1:]
        rest = params[1:]
        processer.cenv.parent[name] = SimpleMacro([args] + rest, processer.cenv.parent)
        return [lambda *x: None]


Globals.Globals['define'] = define()
Globals.Globals['set!'] = Set()
Globals.Globals['define-macro'] = Globals.Globals['defmacro'] = defmacro()
