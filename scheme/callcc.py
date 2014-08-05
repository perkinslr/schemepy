from Queue import Empty
from zope.interface import implements

from scheme.procedure import Procedure
from scheme.processer import Globals


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
        processer.setContinuation([self.continuation, ast[0]])
        ret = processer.process(processer.ast, processer.cenv, 1)
        processer.dumpStack()
        processer.ast=[ret]
        raise Empty()


Globals.Globals['call/cc'] = callcc()
