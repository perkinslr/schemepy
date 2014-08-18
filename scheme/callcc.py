from Queue import Empty
from zope.interface import implements, providedBy
from scheme.macro import Macro

from scheme.procedure import Procedure
from scheme.processer import Globals, processer as p
from scheme.utils import deepcopy, callCCBounce


class callcc():
    implements(Procedure)
    def __init__(self):
        self.env = Globals
    def __call__(self, processer, ast):
        #raise Exception()
        continuation = processer.continuation
        callback = callccCallback(continuation)
        #processer.popStack([ast[0], callback])
        #processer.stackPointer-=1
        print 21, providedBy(ast[0]), ast
        if Procedure in providedBy(ast[0]):
            print 23, ast
            processer.pushStackN()
            r = processer.process([[ast[0], callback]], processer.cenv)
            processer.popStackN()
            print 25, r
        elif Macro in providedBy(ast[0]):
            print 24, ast
            r = ast[0](processer, [callback])
            print 25, r
            processer.pushStackN()
            r = processer.process(r,processer.cenv)
            print 28, r
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
        processer.setContinuation([self.continuation,ast[0]])
        #if processer.callStack.queue:
         #   processer.callStack.queue[-1][2]=self.continuation['stackPointer']
        e=callCCBounce()
        e.ret=processer.process(processer.ast, processer.cenv, max(processer.initialCallDepth, self.continuation['initialCallDepth']+1))
        processer.dumpStack()
        #p.dumpStack()
        raise e



Globals.Globals['call/cc'] = callcc()
