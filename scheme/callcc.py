from zope.interface import implements, providedBy

from scheme.macro import Macro
from scheme.procedure import Procedure
from scheme.processer import Globals, processer as p
from scheme.utils import callCCBounce
from scheme.symbol import Symbol

class CCC(Symbol):
    def isBound(self, *args):
        return True
    def getEnv(self, *args):
        return Globals.Globals
    def toObject(self, *args):
        return callcc()
    
    

class callcc(object):
    implements(Procedure)
    def __init__(self):
        self.env = Globals.Globals
    def __call__(self, *args):
        if len(args) == 1:
            ast=args[0]
            processer = p
        else:
            processer, ast = args
        # raise Exception()
        continuation = processer.continuation
        continuation['initialCallDepth'] += 1
        continuation['targetCallDepth'] = processer.callDepth

        callback = callccCallback(continuation, self)
        # processer.popStack([ast[0], callback])
        # processer.stackPointer-=1
        
        if Procedure in providedBy(ast[0]):
            processer.pushStack([[ast[0], callback]])
            r = processer.process([[ast[0], callback]], processer.cenv)
#            processer.popStack(r)
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
    def __init__(self, continuation, ccc):
        self.env = Globals
        self.continuation = continuation
        self.ccc=ccc
    def __call__(self, *args):
        if len(args) == 1:
            ast=args
            processer = p
        else:
            processer, ast = args
        processer.dumpStack()
        # if processer.callStack.queue:
        #processer.callStack.queue[-1][2]=self.continuation['stackPointer']
        e = callCCBounce()
        e.continuation=self.continuation
        e.retval = ast[0]
        e.ccc=self.ccc
        #e.ret = processer.process(processer.ast, processer.cenv,
        #                          max(processer.initialCallDepth, self.continuation['initialCallDepth'] - 1))
        #processer.dumpStack()
        # p.dumpStack()
        raise e


Globals.Globals['call/cc'] = CCC('call/cc')
