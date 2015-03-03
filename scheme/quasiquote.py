__author__ = 'perkins'

from zope.interface import implements

from scheme.macro import Macro
from scheme.Globals import Globals
from utils import copy_with_quasiquote


class quasiquote(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        env = processer.cenv.parent
        if len(params) > 1:
            raise SyntaxError("quasiquote accepts only 1 argument")
        processer.popStack(copy_with_quasiquote(processer, env, params, o_stack=[])[0][0])
        processer.stackPointer += 1
        return None


Globals['quasiquote'] = quasiquote()