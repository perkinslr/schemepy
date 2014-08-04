from zope import interface


# noinspection PyUnusedLocal
from scheme.environment import Environment
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
    def __call__(self, processer, args):
        retval = None
        env = Environment(self.env)
        if (isinstance(self.ast[0], list)):
            if '.' in self.ast[0]:
                idx = 0
                for idx, item in enumerate(self.ast[0][:-2]):
                    i = args[idx]
                    print 30, item, i
                    env[item] = i
                env[self.ast[0][-1]] = args[idx:]
            else:
                for idx, item in enumerate(self.ast[0]):
                    i = args[idx]
                    env[item] = i
        else:
            env[self.ast[0]] = args[0]
        for i in self.ast[1:]:
            retval = processer.process(deepcopy([i]), env)

        return retval
