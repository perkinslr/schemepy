# cython: profile=True


from Queue import Empty
from collections import deque

from zope.interface import providedBy

from scheme import Globals
from scheme.utils import callCCBounce
from scheme.environment import Environment
from scheme.procedure import Procedure, SimpleProcedure
from scheme.macro import Macro, MacroSymbol
from scheme.utils import deepcopy, expand_quotes
from scheme.symbol import Symbol
from scheme import debug


current_processer = None
discarded_frames=[]
# noinspection PyAttributeOutsideInit
cdef class Processer(object):
    cdef int callDepth
    cdef int _stackPointer
    cdef int _initialCallDepth
    cdef object _children
    cdef object parent
    cdef object _env
    cdef object _ast
    cdef object _cenv
    cdef object callStack

    def getICD(self):
        return self._initialCallDepth
    def setICD(self, icd):
        self._initialCallDepth=icd
    initialCallDepth=property(getICD,setICD)

    def getAst(self):
        return self._ast
    def setAst(self, value):
        self._ast=value
    ast=property(getAst,setAst)

    def getCallDepth(self):
        return self.callDepth
    
    def getChildren(self):
        return self._children
    
    children=property(getChildren)
    
    
    def getStackPointer(self):
        return self._stackPointer
    def setStackPointer(self, val):
        self._stackPointer=val
    stackPointer=property(getStackPointer, setStackPointer)

    def getEnv(self):
        return self._env
    def setEnv(self, val):
        self._env=val

    env=property(getEnv, setEnv)

    def getCenv(self):
        return self._cenv
    def setCenv(self, val):
        self._cenv=val
    cenv=property(getCenv, setCenv)
    
    def __init__(self, parent=None):
#        if current_processer:
#            raise Exception()
        self._children=[]
        self.parent=parent
        if parent is not None:
            self.parent.children.append(self)
        self.callStack = deque()
        self.callDepth = 0
        self._env = Globals.Globals
        self._ast = None
        self._stackPointer = 0
        self.cenv = None
        self._initialCallDepth = 0
    def getContinuation(self):
        if self.parent:
            pc = self.parent.continuation
        else:
            pc=dict(callDepth=0, callStack=[], initialCallDepth=0)
        return dict(env=self.cenv, callDepth=self.callDepth+pc['callDepth'], callStack=deepcopy(list(self.callStack))+pc['callStack'],
                    initialCallDepth=self._initialCallDepth+pc['initialCallDepth'], stackPointer=self._stackPointer)
    def setContinuation(self, args):
        (continuation, retval) = args
        self.callStack = deque(deepcopy(continuation['callStack']))
        self.callDepth = continuation['callDepth']
        self.cenv = continuation['env']
        self._stackPointer = continuation['stackPointer']
        self.popStack(retval)
    continuation = property(getContinuation, setContinuation)
    def pushStackN(self):
        self.callStack.append((self._ast, self.cenv, self._stackPointer, 0))
        self.callDepth += 1
    def popStackN(self):
        self._ast, self.cenv, self._stackPointer, garbage = self.callStack.pop()
        self.callDepth -= 1
    def pushStack(self, ast):
        self.callStack.append((self._ast, self.cenv, self._stackPointer, 1))
        self._ast = ast
        self.cenv = Environment(self.cenv)
        self._stackPointer = 0
        self.callDepth += 1
    def popStack(self, retval):
        if isinstance(retval, Symbol):
            retval=MacroSymbol(retval).setEnv({retval:retval.toObject(self.cenv)})
        if debug.DEBUG:
            discarded_frames.append((self._ast, self.cenv, self._stackPointer))
        self._ast, self.cenv, self._stackPointer, rv = self.callStack.pop()
        self.callDepth -= 1
        if rv:
           self._ast[self._stackPointer] = retval
    def dumpStack(self):
        while self.callDepth > 0 and len(self.callStack):
            self.popStackN()
        self._stackPointer=0
        self.cenv=None
        self._initialCallDepth=0
        self._ast=None
        self.callDepth=0
    def _process(self, _ast, env=None, callDepth=None):
        try:
            return self.process(_ast, env, callDepth)
        except callCCBounce as e:
            # noinspection PyUnresolvedReferences
            return e.ret
        except Empty as e:
            if ('cont' in dir(e)):
                # noinspection PyUnresolvedReferences
                continuation = e.cont
                # noinspection PyUnresolvedReferences
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
                self._initialCallDepth = callDepth
            else:

                self._initialCallDepth = self.callDepth

            if env is None:
                self.cenv = self._env
            else:
                self.cenv = env
            self._ast = _ast
            self._ast=expand_quotes(self._ast)
            self._stackPointer = 0;
            if not isinstance(self._ast, list):
                if isinstance(self._ast, Symbol):
                    this = self._ast.toObject(self.cenv)
                else:
                    this = self._ast
                if self.callDepth:
                    self.popStack(this)
                else:
                    return this
            if len(self._ast)==1 and not isinstance(self._ast[0], list):
                if isinstance(self._ast[0], Symbol):
                    this = self._ast[0].toObject(self.cenv)
                else:
                    this = self._ast[0]
                if self.callDepth:
                    self.popStack(this)
                else:
                    return this
            while True:
                if self._stackPointer >= len(self._ast) and self.callDepth <= self._initialCallDepth:
                    return self._ast[-1]
                if self._stackPointer >= len(self._ast):
                    for idx, i in enumerate(self._ast):
                        if isinstance(i, Symbol) and i.isBound(self.cenv, True):
                            self._ast[idx]=i.toObject(self.cenv)
                    initial_call_depth = self._initialCallDepth
                    if isinstance(self._ast[0], Symbol):
                        self._ast[0] = self._ast[0].toObject(self.cenv)
                    if isinstance(self._ast[0], SimpleProcedure):
                        this=self._ast[0]
                        args=self._ast[1:]
                        params=deepcopy(this.ast[0])
                        e = Environment(this.env)
                        if isinstance(params, list):
                            if '.' in params:
                                iter_args = iter(args)
                                for idx, item in enumerate(params[:-2]):
                                    e[item] = iter_args.next()
                                e[params[-1]] = list(iter_args)
                            else:
                                if (isinstance(args, list) and len(args) != len(params)):
                                    raise TypeError("%r expected exactly %i arguments, got %i" % (
                                        self, len(self._ast[0]), len(args)))
                                if (not isinstance(args, list) and 1 != len(params)):
                                    raise TypeError("%r expected exactly %i arguments, got %i" % (
                                        self, len(self._ast[0]), 1))
                                iter_args = iter(args)
                                for idx, item in enumerate(params):
                                    e[item] = iter_args.next()
                        else:
                            e[params] = args
                        self.popStackN()
                        self.pushStack(deepcopy([Symbol('last'), [Symbol('list')] + this.ast[1:]]))
                        self.cenv = Environment(e)
                        continue
                    elif Procedure in providedBy(self._ast[0]):
                        self.popStack(self._ast[0](self, self._ast[1:]))
                    elif Macro in providedBy(self._ast[0] if not isinstance(self._ast[0], Symbol) else self._ast[0].toObject(self._cenv)):
                        initial_call_depth = self._initialCallDepth
                        r = self._ast[0](self, self._ast[1:])
                        self._initialCallDepth = initial_call_depth
                        if r is None:
                            continue
                        if not isinstance(r, list):
                            r1 = [lambda *x: r]
                            self._ast[:] = r1
                        else:
                            self._ast[:] = r
                        continue
                    else:
                        r = self._ast[0](*self._ast[1:])
                        self.popStack(r)
                    self._initialCallDepth = initial_call_depth
                    self._stackPointer+=1
                    continue
                this = self._ast[self._stackPointer]
                if isinstance(this, list):
                    self.pushStack(this)
                    continue
                if isinstance(this, Symbol) and this.isBound(self.cenv):
                    t = this.toObject(self.cenv)
                    while isinstance(t, Symbol) and t.isBound(self.cenv):
                        t = t.toObject(self.cenv)
                else:
                    t = this
                if self._stackPointer == 0 and Macro in providedBy(t):
                    initial_call_depth = self._initialCallDepth
                    r = t(self, self._ast[1:])
                    self._initialCallDepth = initial_call_depth
                    if r is None:
                        continue
                    if not isinstance(r, list):
                        r1 = [lambda *x: r]
                        self._ast[:] = r1
                    else:
                        self._ast[:] = r
                    continue
                if isinstance(this, Symbol) and this.isBound(self.cenv):
                    self._ast[self._stackPointer] = this.toObject(self.cenv)
                self._stackPointer += 1
        except IndexError as e:
            if hasattr(e, 'ret'):
                return e.ret
            return self._ast[-1]





processer=Processer()
