__author__ = 'perkins'

from scheme.macro import Macro
from scheme.Globals import Globals
from zope.interface import implements


class let_aster(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        env = processer.cenv
        bindings = params[0]
        for binding in bindings:
            if len(binding[1:]) != 1:
                raise SyntaxError("let requires a list of pairs for its first argument")
            env[binding[0]] = processer.process([binding[1]], env)
        processer.process(params[1:], env)
        return


Globals['let*'] = let_aster()