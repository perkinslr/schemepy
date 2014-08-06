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
from scheme import debug

callStack = LifoQueue()

class Processer:
    def __init__(self, parent=None):
        self.parent=parent
        self.callStack = LifoQueue()
        self.callDepth = 0
        self.env = Globals.Globals
        self.ast = None
        self.stackPointer = 0
        self.cenv = None
        self.initialCallDepth = 0
    def getContinuation(self):
        if self.parent:
            pc = self.parent.continuation
        else:
            pc=dict(callDepth=0, callStack=[])
        return dict(env=self.cenv, callDepth=self.callDepth+pc['callDepth'], callStack=deepcopy(self.callStack.queue)+pc['callStack'],
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
        while self.callDepth > 0 and self.callStack.queue:
            self.popStack(None)
        self.stackPointer=0
        self.cenv=None
        self.initialCallDepth=0
        self.ast=None
        self.callDepth=0
    def _process(self, _ast, env=None, callDepth=None):
        try:
            return self.process(_ast, env, callDepth)
        except Empty as e:
            if ('cont' in dir(e)):
                continuation = e.cont
                retval=e.ret
                self.setContinuation([continuation, retval])
                return self._process(processer.ast, processer.cenv, 1)
            raise e
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
                if isinstance(self.ast, Symbol):
                    this = self.ast.toObject(self.cenv)
                else:
                    this = self.ast
                if self.callDepth:
                    self.popStack(this)
                else:
                    return this
            if len(self.ast)==1 and not isinstance(self.ast[0], list):
                if isinstance(self.ast[0], Symbol):
                    this = self.ast[0].toObject(self.cenv)
                else:
                    this = self.ast[0]
                if self.callDepth:
                    self.popStack(this)
                else:
                    return this
            while True:
                if (isinstance(self.ast, list)):
                    for idx, this in enumerate(self.ast):
                        if this == "'":
                            quoteTarget=self.ast.pop(idx+1)
                            if quoteTarget=="'":
                                def getQuoteTarget():
                                    qt = self.ast.pop(idx+1)
                                    if qt == "'":
                                        return [Symbol('quote'), getQuoteTarget()]
                                    return qt
                                quoteTarget=[Symbol('quote'), getQuoteTarget()]
                            self.ast[idx]=[Symbol('quote'), quoteTarget]
                        elif this == "`":
                            quoteTarget=self.ast.pop(idx+1)
                            if quoteTarget=="`":
                                def getQuoteTarget():
                                    qt = self.ast.pop(idx+1)
                                    if qt == "`":
                                        return [Symbol('quasiquote'), getQuoteTarget()]
                                    return qt
                                quoteTarget=[Symbol('quasiquote'), getQuoteTarget()]
                            self.ast[idx]=[Symbol('quasiquote'), quoteTarget]
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
                    while isinstance(t, Symbol) and t.isBound(self.cenv):
                        t = t.toObject(self.cenv)
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
                        if debug.DEBUG:
                            e=Exception()
                            e.r=r
                            raise e
                        self.ast[:] = r
                    self.initialCallDepth = initial_call_depth
                    continue
                if isinstance(this, Symbol) and this.isBound(self.cenv):
                    self.ast[self.stackPointer] = this.toObject(self.cenv)

                self.stackPointer += 1
        except Empty as e:
            if 'ret' in dir(e):
                return e.ret
            return self.ast[-1]
            raise e





processer=Processer()