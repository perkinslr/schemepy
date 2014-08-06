from Queue import Empty
from zope.interface import implements

from scheme.procedure import Procedure
from scheme.processer import Globals, processer as p
from scheme.utils import deepcopy


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
        global c
        c=deepcopy(self.continuation['callStack'])
        p1 = processer.__class__()
        p1.setContinuation([self.continuation, ast[0]])
        ret = p1.process(p1.ast, p1.cenv, 0)
        processer.dumpStack()
        p.dumpStack()
        p.ast=[ret]
        processer.ast=[ret]
        e=Empty()
        e.ret=ret
        raise e


Globals.Globals['call/cc'] = callcc()
