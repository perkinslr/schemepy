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
        continuation['targetCallDepth'] = processer.callDepth
        callback = callccCallback(continuation)
        # processer.popStack([ast[0], callback])
        # processer.stackPointer-=1
        if Procedure in providedBy(ast[0]):
            cd = processer.callDepth
            processer.pushStack([ast[0], callback])
            r = processer.process([[ast[0], callback]], processer.cenv)
            processer.popStackN()
        elif Macro in providedBy(ast[0]):
            r = ast[0](processer, [callback])
            processer.pushStack(r)
            r = processer.process(r, processer.cenv)
            processer.popStack(r)
        else:
            r = ast[0](callback)
        return r


class callccCallback():
    implements(Procedure)
    def __init__(self, continuation):
        self.env = Globals
        self.continuation = continuation
    def __call__(self, processer, ast):
        processer.dumpStack()
        # if processer.callStack.queue:
        #processer.callStack.queue[-1][2]=self.continuation['stackPointer']
        e = callCCBounce()
        e.continuation=self.continuation
        e.retval = ast[0]
        #e.ret = processer.process(processer.ast, processer.cenv,
        #                          max(processer.initialCallDepth, self.continuation['initialCallDepth'] - 1))
        #processer.dumpStack()
        # p.dumpStack()
        raise e


Globals.Globals['call/cc'] = callcc()
