from scheme.symbol import Symbol


__author__ = 'perkins'

from scheme.macro import Macro
from scheme.Globals import Globals
from zope.interface import implements


class IF(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        if (len(params)) > 3:
            raise SyntaxError("if accepts a maximum of 3 params")
        conditional = params[0]
        if_true = params[1]
        if_false = params[2] if len(params) == 3 else False
        env = processer.cenv
        if isinstance(conditional, list):
            old_stack_pointer = processer.stackPointer
            processer.stackPointer = 1
            processer.pushStack(conditional)
            # noinspection PyTypeChecker
            ret = processer.__class__(processer).process([Symbol('Begin')] + [conditional], env)
            processer.popStack(ret)
            processer.stackPointer = old_stack_pointer
            if ret:
                return if_true
            else:
                return if_false
        else:
            if (isinstance(conditional, Symbol) and conditional.toObject(env)) or (
                    not isinstance(conditional, Symbol) and conditional):
                return if_true
            else:
                return if_false


Globals['if'] = IF()