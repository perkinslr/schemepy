__author__ = 'lperkins2'

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
        for idx, param in enumerate(params):
            processer.stackPointer+=1
            icd = processer.callDepth
            processer.pushStack([param])
            retval = processer.process([param], env, processer.callDepth)
#            while processer.callDepth > icd:
#                processer.popStackN()
            processer.popStack(retval)
            params[idx]=retval
        processer.popStack(retval)
        processer.stackPointer += 1
        return


Globals['begin'] = begin()
