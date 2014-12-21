__author__ = 'perkins'

from zope.interface import implements

from scheme.macro import Macro
from scheme.Globals import Globals
from utils import copy_with_quasisyntax
from scheme.syntax import SyntaxSymbol

class quasisyntax(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        env = processer.cenv.parent
        if len(params) > 1:
            raise SyntaxError("quasisyntax accepts only 1 argument")
        o = copy_with_quasisyntax(processer, env, params, o_stack=[])
        o = SyntaxSymbol(o[0][0]).setSymbol(o[0][0])
        processer.popStack(o,False)
        processer.stackPointer += 1
        return None


Globals['quasisyntax'] = quasisyntax()
