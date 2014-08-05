__author__ = 'jeanie'

from scheme.Globals import Globals
from zope.interface import implements
from scheme.macro import Macro


class begin(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        env = processer.cenv
        #for param in params[:-1]:
        #    processer.process(param, env)
        for param in params[:-1]:
            processer.process([param], env.parent)
        ret = processer.process([params[-1]], env.parent)
        processer.popStack(ret)
        processer.stackPointer+=1
        return


Globals['begin'] = begin()