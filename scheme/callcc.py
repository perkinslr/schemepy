from Queue import Empty
from zope.interface import implements, providedBy

from scheme.procedure import Procedure
from scheme.processer import Globals, processer as p
from scheme.utils import deepcopy, callCCBounce


class callcc():
    implements(Procedure)
    def __init__(self):
        self.env = Globals
    def __call__(self, processer, ast):
        continuation = processer.continuation
        callback = callccCallback(continuation)
        r = ast[0](processer, [callback])
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
        e=callCCBounce()
        e.ret=processer.process(processer.ast, processer.cenv, 0)
        processer.dumpStack
        raise e


        '''global c
        c=deepcopy(self.continuation['callStack'])
        p1 = processer.__class__()
        p1.setContinuation([self.continuation, ast[0]])
        ret = p1.process(p1.ast, p1.cenv, 0)
        processer.dumpStack()
        p.dumpStack()
        p.ast=[ret]
        processer.ast=[ret]'''


Globals.Globals['call/cc'] = callcc()
