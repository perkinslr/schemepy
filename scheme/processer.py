from scheme import Globals
from scheme.utils import callCCBounce
from scheme.environment import Environment
from scheme.procedure import Procedure, SimpleProcedure
from scheme.macro import Macro, MacroSymbol
from scheme.utils import deepcopy, expand_quotes
from zope.interface import providedBy
from scheme.symbol import Symbol
from Queue import LifoQueue, Empty
from scheme import debug

current_processer = None
discarded_frames=[]
class Processer:
    def __init__(self, parent=None):
#        if current_processer:
#            raise Exception()
        self.children=[]
        self.parent=parent
        if parent:
            parent.children.append(self)
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
            pc=dict(callDepth=0, callStack=[], initialCallDepth=0)
        return dict(env=self.cenv, callDepth=self.callDepth+pc['callDepth'], callStack=deepcopy(self.callStack.queue)+pc['callStack'],
                    initialCallDepth=self.initialCallDepth+pc['initialCallDepth'], stackPointer=self.stackPointer)
    def setContinuation(self, (continuation, retval)):
        self.callStack.queue[:] = deepcopy(continuation['callStack'])
        self.callDepth = continuation['callDepth']
        self.cenv = continuation['env']
        self.stackPointer = continuation['stackPointer']
        self.popStack(retval)
    continuation = property(getContinuation, setContinuation)
    def pushStackN(self):
        self.callStack.put((self.ast, self.cenv, self.stackPointer, 0))
        self.callDepth += 1
    def popStackN(self):
        self.ast, self.cenv, self.stackPointer, garbage = self.callStack.get_nowait()
        self.callDepth -= 1
    def pushStack(self, ast):
        self.callStack.put((self.ast, self.cenv, self.stackPointer, 1))
        self.ast = ast
        self.cenv = Environment(self.cenv)
        self.stackPointer = 0
        self.callDepth += 1
    def popStack(self, retval):
        if isinstance(retval, Symbol):
            retval=MacroSymbol(retval).setEnv({retval:retval.toObject(self.cenv)})
        if debug.DEBUG:
            discarded_frames.append((self.ast, self.cenv, self.stackPointer))
        self.ast, self.cenv, self.stackPointer, rv = self.callStack.get_nowait()
        self.callDepth -= 1
        if rv:
           self.ast[self.stackPointer] = retval
    def dumpStack(self):
        while self.callDepth > 0 and self.callStack.queue:
            self.popStackN()
        self.stackPointer=0
        self.cenv=None
        self.initialCallDepth=0
        self.ast=None
        self.callDepth=0
    def _process(self, _ast, env=None, callDepth=None):
        try:
            return self.process(_ast, env, callDepth)
        except callCCBounce as e:
            return e.ret
        except Empty as e:
            if ('cont' in dir(e)):
                continuation = e.cont
                retval=e.ret
                self.setContinuation([continuation, retval])
                return self._process(processer.ast, processer.cenv, 1)
            raise e
    def process(self, _ast, env=None, callDepth=None):
        global current_processer
        current_processer = self
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
            self.ast=expand_quotes(self.ast)
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
                if self.stackPointer >= len(self.ast) and self.callDepth <= self.initialCallDepth:
                    return self.ast[-1]
                if self.stackPointer >= len(self.ast):
                    for idx, i in enumerate(self.ast):
                        if isinstance(i, Symbol) and i.isBound(self.cenv):
                            self.ast[idx]=i.toObject(self.cenv)
                    initial_call_depth = self.initialCallDepth
                    if isinstance(self.ast[0], Symbol):
                        self.ast[0] = self.ast[0].toObject(self.cenv)
                    if isinstance(self.ast[0], SimpleProcedure):
                        this=self.ast[0]
                        args=self.ast[1:]
                        params=deepcopy(this.ast[0])
                        e = Environment(this.env)
                        print 148, params, args
                        if isinstance(params, list):
                            if '.' in params:
                                iterargs = iter(args)
                                for idx, item in enumerate(params[:-2]):
                                    e[item] = iterargs.next()
                                e[params[-1]] = list(iterargs)
                            else:
                                print self.ast
                                print args
                                if (isinstance(args, list) and len(args) != len(params)):
                                    raise TypeError("%r expected exactly %i arguments, got %i" % (
                                        self, len(self.ast[0]), len(args)))
                                if (not isinstance(args, list) and 1 != len(params)):
                                    raise TypeError("%r expected exactly %i arguments, got %i" % (
                                        self, len(self.ast[0]), 1))
                                iterargs = iter(args)
                                for idx, item in enumerate(params):
                                    e[item] = iterargs.next()
                        else:
                            e[params] = args
                        print 161, self.ast
                        self.popStackN()
                        print 163, self.ast
                        self.pushStack(deepcopy([Symbol('last'), [Symbol('list')] + this.ast[1:]]))
                        print 162, self.ast, e
                        self.cenv = Environment(e)
                        continue
                    elif Procedure in providedBy(self.ast[0]):
                        self.popStack(self.ast[0](self, self.ast[1:]))
                    else:
                        r = self.ast[0](*self.ast[1:])
                        self.popStack(r)
                    self.initialCallDepth = initial_call_depth
                    self.stackPointer+=1
                    continue
                this = self.ast[self.stackPointer]
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