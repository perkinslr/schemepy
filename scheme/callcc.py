from zope.interface import implements, providedBy

from scheme.macro import Macro
from scheme.procedure import Procedure
from scheme.processer import Globals, processer as p
from scheme.utils import callCCBounce


class callcc():
    implements(Procedure)
    def __init__(self):
        self.env = Globals
    def __call__(self, processer, ast):
        # raise Exception()
        continuation = processer.continuation
        continuation['initialCallDepth'] += 1
        callback = callccCallback(continuation)
        # processer.popStack([ast[0], callback])
        # processer.stackPointer-=1
        if Procedure in providedBy(ast[0]):
            processer.pushStackN()
            r = processer.process([[ast[0], callback]], processer.cenv)
            processer.popStackN()
        elif Macro in providedBy(ast[0]):
            r = ast[0](processer, [callback])
            processer.pushStackN()
            r = processer.process(r, processer.cenv)
            processer.popStackN()
        else:
            r = ast[0](callback)
        return r


class callccCallback():
    implements(Procedure)
    def __init__(self, continuation):
        self.env = Globals
        self.continuation = continuation
    def __call__(self, processer, ast):
        p.dumpStack()
        processer.dumpStack()
        processer.setContinuation([self.continuation, ast[0]])
        # if processer.callStack.queue:
        # processer.callStack.queue[-1][2]=self.continuation['stackPointer']
        e = callCCBounce()
        e.ret = processer.process(processer.ast, processer.cenv,
                                  max(processer.initialCallDepth, self.continuation['initialCallDepth'] - 1))
        processer.dumpStack()
        # p.dumpStack()
        raise e


Globals.Globals['call/cc'] = callcc()
