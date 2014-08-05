import sys

from scheme import Globals


sys.path.extend('/home/perkins/pycharm')

from scheme.environment import Environment
from scheme.procedure import Procedure
from scheme.macro import Macro
from scheme.utils import deepcopy
from zope.interface import providedBy
from scheme.symbol import Symbol
from Queue import LifoQueue, Empty


class Processer:
    def __init__(self):
        self.callStack = LifoQueue()
        self.callDepth = 0
        self.env = Globals.Globals
        self.ast = None
        self.stackPointer = 0
        self.cenv = None
        self.initialCallDepth = 0
    def getContinuation(self):
        return dict(env=self.cenv, callDepth=self.callDepth, callStack=deepcopy(self.callStack.queue),
                    initialCallDepth=self.initialCallDepth, stackPointer=self.stackPointer)
    def setContinuation(self, (continuation, retval)):

        self.callStack.queue[:] = continuation['callStack']
        self.callDepth = continuation['callDepth']
        self.cenv = continuation['env']
        self.stackPointer = continuation['stackPointer']
        self.popStack(retval)

    continuation = property(getContinuation, setContinuation)
    def pushStack(self, ast):

        self.callStack.put((self.ast, self.cenv, self.stackPointer))
        self.ast = ast
        self.cenv = Environment(self.cenv)
        self.stackPointer = 0
        self.callDepth += 1
    def popStack(self, retval):

        self.ast, self.cenv, self.stackPointer = self.callStack.get_nowait()
        self.callDepth -= 1
        self.ast[self.stackPointer] = retval
    def dumpStack(self):
        while self.callDepth > 0:
            self.popStack(None)
        self.stackPointer=0
        self.cenv=None
        self.initialCallDepth=0
        self.ast=None
        self.callDepth=0
    def process(self, _ast, env=None, callDepth=None):
        if _ast==[[]]:
            raise SyntaxError()
        """


        :rtype : object
        :param _ast:
        :param env: Environment
        :return:
        """
        try:
            if callDepth is not None:

                self.initialCallDepth = callDepth
            else:

                self.initialCallDepth = self.callDepth

            if env is None:
                self.cenv = self.env
            else:
                self.cenv = env
            self.ast = _ast
            self.stackPointer = 0;
            if not isinstance(self.ast, list):
                if self.callDepth:
                    self.popStack(self.ast.toObject(self.cenv))
                else:
                    return self.ast.toObject(self.cenv)

            while True:
                if self.stackPointer >= len(self.ast) and self.callDepth <= self.initialCallDepth:
                    return self.ast[-1]
                if self.stackPointer >= len(self.ast):
                    for idx, i in enumerate(self.ast):
                        if isinstance(i, Symbol):
                            self.ast[idx]=i.toObject(self.cenv)
                    initial_call_depth = self.initialCallDepth
                    if isinstance(self.ast[0], Symbol):
                        self.ast[0] = self.ast[0].toObject(self.cenv)
                    if Procedure in providedBy(self.ast[0]):
                        self.popStack(self.ast[0](self, self.ast[1:]))
                    else:
                        r = self.ast[0](*self.ast[1:])
                        self.popStack(r)
                    self.initialCallDepth = initial_call_depth
                    self.stackPointer+=1
                    continue
                this = self.ast[self.stackPointer]
                if this == "'":
                    quoteTarget=self.ast.pop(self.stackPointer+1)
                    if quoteTarget=="'":
                        def getQuoteTarget():
                            qt = self.ast.pop(self.stackPointer+1)
                            if qt == "'":
                                return [Symbol('quote'), getQuoteTarget()]
                            return qt
                        quoteTarget=[Symbol('quote'), getQuoteTarget()]
                    self.ast[self.stackPointer]=[Symbol('quote'), quoteTarget]
                    continue
                elif this == "`":

                    quoteTarget=self.ast.pop(self.stackPointer+1)
                    if quoteTarget=="`":
                        def getQuoteTarget():
                            qt = self.ast.pop(self.stackPointer+1)
                            if qt == "`":
                                return [Symbol('quasiquote'), getQuoteTarget()]
                            return qt
                        quoteTarget=[Symbol('quasiquote'), getQuoteTarget()]
                    self.ast[self.stackPointer]=[Symbol('quasiquote'), quoteTarget]

                    continue
                elif this == ",":

                    quoteTarget=self.ast.pop(self.stackPointer+1)
                    if quoteTarget==",":
                        def getQuoteTarget():
                            qt = self.ast.pop(self.stackPointer+1)
                            if qt == ",":
                                return [Symbol('unquote'), getQuoteTarget()]
                            return qt
                        quoteTarget=[Symbol('unquote'), getQuoteTarget()]
                    self.ast[self.stackPointer]=[Symbol('unquote'), quoteTarget]
                    continue
                if isinstance(this, list):
                    self.pushStack(this)
                    continue
                if isinstance(this, Symbol) and this.isBound(self.cenv):
                    t = this.toObject(self.cenv)
                else:
                    t = this
                if self.stackPointer == 0 and Macro in providedBy(t):
                    initial_call_depth = self.initialCallDepth
                    r = t(self, self.ast[1:])
                    if r is None:
                        self.initialCallDepth = initial_call_depth
                        continue
                    if not isinstance(r, list):
                        r1 = [lambda *x: r]
                        self.ast[:] = r1
                    else:
                        self.ast[:] = r
                    self.initialCallDepth = initial_call_depth
                    continue
                if isinstance(this, Symbol) and this.isBound(self.cenv):
                    self.ast[self.stackPointer] = this.toObject(self.cenv)

                self.stackPointer += 1
        except Empty:
            print "Rising from call/cc"
            return self.ast[-1]




processer=Processer()