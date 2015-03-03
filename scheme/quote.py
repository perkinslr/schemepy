__author__ = 'perkins'

from zope.interface import implements

from scheme.macro import Macro
from scheme.Globals import Globals
from utils import copy_with_quote


class quote(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        if len(params) > 1:
            raise SyntaxError("quote accepts only 1 argument")
        processer.popStack(copy_with_quote(params)[0])
        processer.stackPointer += 1
        return None


Globals['quote'] = quote()