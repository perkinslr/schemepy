from scheme.symbol import Symbol


__author__ = 'jeanie'

from scheme.Globals import Globals
from zope.interface import implements
from scheme.macro import Macro


class begin(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        env=processer.cenv.parent
        retval = None
        for param in params:
            processer.pushStackN()
            print 20, processer.callDepth, param, processer.ast
            retval = processer.process([param], env, processer.callDepth)
            print 21, retval
            processer.popStackN()
        processer.popStack(retval)
        processer.stackPointer+=1
        return


Globals['begin'] = begin()