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
        for param in params:
            retval = processer.__class__(processer).process([param], processer.cenv.parent)

        processer.popStack(retval)
        processer.stackPointer+=1
        return


Globals['begin'] = begin()