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
        self.macros = dict(Globals.Macros)
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
    def process(self, _ast, env=None, callDepth=None):
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
                if self.stackPointer >= len(self.ast) and self.callDepth == self.initialCallDepth:
                    return self.ast[-1]
                if self.stackPointer >= len(self.ast):
                    initial_call_depth = self.initialCallDepth
                    if isinstance(self.ast[0], Symbol):
                        self.ast[0] = self.ast[0].toObject(self.cenv)
                    if Procedure in providedBy(self.ast[0]):

                        self.popStack(self.ast[0](self, self.ast[1:]))
                    else:
                        self.popStack(self.ast[0](*self.ast[1:]))
                    self.initialCallDepth = initial_call_depth
                    continue
                this = self.ast[self.stackPointer]
                if isinstance(this, list):
                    self.pushStack(this)
                    continue
                if isinstance(this, Symbol) and this.isBound(self.cenv):
                    t = this.toObject(self.cenv)
                else:
                    t = this;
                if self.stackPointer == 0 and Macro in providedBy(t):
                    initial_call_depth = self.initialCallDepth
                    r = t(self, self.ast[1:])
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




