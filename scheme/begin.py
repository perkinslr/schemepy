__author__ = 'jeanie'

from zope.interface import implements

from scheme.Globals import Globals
from scheme.macro import Macro


class begin(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        env = processer.cenv.parent
        retval = None
        for param in params:
            processer.pushStack([param])
            retval = processer.doProcess([param], env, processer.callDepth)
            processer.popStack(retval)
        processer.popStack(retval)
        processer.stackPointer += 1
        return


Globals['begin'] = begin()
