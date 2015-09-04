from scheme import Globals
from scheme.syntax_rules import SyntaxSymbol
from scheme.utils import callCCBounce
from scheme.environment import Environment
from scheme.procedure import Procedure, SimpleProcedure
from scheme.macro import Macro, MacroSymbol
from scheme.utils import deepcopy, expand_quotes
import scheme.utils
from zope.interface import providedBy
from scheme.symbol import Symbol
from Queue import LifoQueue, Empty
from scheme import debug
from scheme.debug import LOG

current_processer = None
discarded_frames = []


class Processer(object):
    def __init__(self, parent=None):
#        if current_processer:
#            raise Exception()
        self.children = []
        self.parent = parent
        if parent:
            parent.children.append(self)
        self.callStack = LifoQueue()
        self.callDepth = 0
        self.env = Globals.Globals
        self.ast = None
        self.stackPointer = 0
        self.cenv = None
        self.initialCallDepth = 0
        self.shouldAbort = None
    def getContinuation(self):
        if self.parent:
            pc = self.parent.continuation
        else:
            pc = dict(callDepth=0, callStack=[], initialCallDepth=0)
        return dict(env=self.cenv, callDepth=self.callDepth + pc['callDepth'],
                    callStack=deepcopy(self.callStack.queue) + pc['callStack'],
                    initialCallDepth=self.initialCallDepth + pc['initialCallDepth'], stackPointer=self.stackPointer)
    def setContinuation(self, args):
        continuation, retval = args
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
        if debug.getDebug('pushStack'):
            import traceback
            traceback.print_stack()
            print 'push', self.ast, self.stackPointer
        self.callStack.put((self.ast, self.cenv, self.stackPointer, 1))
        self.ast = ast
        self.cenv = Environment(self.cenv)
        self.stackPointer = 0
        self.callDepth += 1
    def popStack(self, retval, wrap=True):
        if debug.getDebug('popStack'):
            import traceback


            traceback.print_stack()
            print 'pop', self.ast, retval, self.stackPointer,
            if len(self.callStack.queue):
                print self.callStack.queue[-1][0], self.callStack.queue[-1][2]
            print
            print
        if isinstance(retval, Symbol) and wrap:
            if isinstance(retval, SyntaxSymbol):
                retval = MacroSymbol(retval).setObj(retval)
            else:
                retval = MacroSymbol(retval).setEnv({retval: retval.toObject(self.cenv)})
        if debug.getDebug('discardedFrames'):
            discarded_frames.append((self.ast, self.cenv, self.stackPointer))
        try:
            self.ast, self.cenv, self.stackPointer, rv = self.callStack.get_nowait()
        except Empty as e:
            e.ret = e.retval = self.ast[-1]
            raise e
        self.callDepth -= 1
        if rv:
            if self.stackPointer >= len(self.ast):
                self.popStack(retval)
            self.ast[self.stackPointer] = retval
        LOG('popStack', self.ast, self.stackPointer)
    def dumpStack(self):
        while self.callDepth > 0 and self.callStack.queue:
            self.popStackN()
        self.stackPointer = 0
        self.cenv = None
        self.initialCallDepth = 0
        self.ast = None
        self.callDepth = 0
    tcd = 0
    def doProcess(self, _ast, env=None, callDepth=None, ccc=False, quotesExpanded=False):
        if not ccc:
            self.dumpStack()
        try:
            return self.process(_ast, env, callDepth, quotesExpanded)
        except callCCBounce as e:
            print >> open('/tmp/ccc.log', 'a'), (e.continuation, e.retval)
            # noinspection PyUnresolvedReferences
            continuation = e.continuation
            callDepth = self.callDepth
            icd = self.initialCallDepth
            self.dumpStack()
            self.callStack.queue = deepcopy(continuation['callStack'])
            self.callDepth = continuation['callDepth']
            self.initialCallDepth = 0
            LOG('call/cc bounce', 109, self.ast)
            self.ast, self.cenv, self.stackPointer, rv = self.callStack.get_nowait()
            # self.callStack.queue.pop(0)
            #self.callDepth-=1
            LOG('call/cc bounce', self.ast)
            seek = True
            while True:
                for i in xrange(len(self.ast)):
                    if isinstance(self.ast[i], list):
                        if isinstance(self.ast[i], list) and self.ast[i][0] is e.ccc:
                            self.ast[i] = e.retval
                            self.stackPointer = i + 1
                            #a = self.ast
                            #self.popStackN()
                            #self.ast=a
                            seek = False
                            break
                if not seek:
                    break
                self.ast, self.cenv, self.stackPointer, rv = self.callStack.get_nowait()

            self.tcd += 1
            while self.callDepth > 1:
                try:
                    self.doProcess(self.ast, self.cenv, 0, True)
                except TypeError as e3:
                    if not callable(self.ast[0]):
                        try:
                            self.popStack(self.ast[-1])
                        except Empty as e5:
                            if hasattr(e5, 'ret'):
                                return e5.ret
                            if hasattr(e5, 'retval'):
                                return e5.retval
                            raise e5
                        #return self.doProcess(self.ast, self.cenv, 0, True)
                    else:
                        raise e3
                        print 157, self.ast, self.stackPointer, self.callStack.queue, self.callDepth
                except Empty as e4:
                    if hasattr(e4, 'ret'):
                        return e4.ret
                    if hasattr(e4, 'retval'):
                        return e4.retval
                    raise e4
            return self.ast[-1]
        except Empty as e1:
            if hasattr(e1, 'ret'):
                return e1.ret
            if hasattr(e1, 'retval'):
                self.dumpStack()
                return e1.retval
            raise e1
    def process(self, _ast, env=None, callDepth=None, quotesExpanded=True):
        global current_processer
        current_processer = self
        if _ast == [[]]:
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
            if not quotesExpanded:
                self.ast = expand_quotes(self.ast)
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
            if len(self.ast) == 1 and not isinstance(self.ast[0], list):
                if isinstance(self.ast[0], Symbol):
                    this = self.ast[0].toObject(self.cenv)
                else:
                    this = self.ast[0]
                if self.callDepth > self.initialCallDepth:
                    self.popStack(this)
                else:
                    return this
            while True:
                if self.shouldAbort:
                    raise self.shouldAbort
                if self.stackPointer >= len(self.ast) and self.callDepth <= self.initialCallDepth:
                    return self.ast[-1]
                if self.stackPointer >= len(self.ast):
                    for idx, i in enumerate(self.ast):
                        if isinstance(i, Symbol) and i.isBound(self.cenv):
                            self.ast[idx] = i.toObject(self.cenv)
                    initial_call_depth = self.initialCallDepth
                    if isinstance(self.ast[0], Symbol):
                        self.ast[0] = self.ast[0].toObject(self.cenv)
                    if isinstance(self.ast[0], SimpleProcedure):
                        this = self.ast[0]
                        args = self.ast[1:]
                        params = deepcopy(this.ast[0])
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
                                        self.ast[0], len(params), len(args)))
                                if (not isinstance(args, list) and 1 != len(params)):
                                    raise TypeError("%r expected exactly %i arguments, got %i" % (
                                        self.ast[0], len(params), len(args)))
                                iter_args = iter(args)
                                for idx, item in enumerate(params):
                                    e[item] = iter_args.next()
                        else:
                            e[params] = args
                        self.popStackN()
                        self.pushStack(deepcopy([Symbol('last'), [Symbol('list')] + this.ast[1:]]))
                        self.cenv = Environment(e)
                        continue
                    elif Procedure in providedBy(self.ast[0]):
                        r = self.ast[0](self, self.ast[1:])
                        self.popStack(r)
                    elif Macro in providedBy(self.ast[0]):
                        r = self.ast[0](self, self.ast[1:])
                        if r is None:
                            continue
                        self.popStack(r)
                    else:
                        r = self.ast[0](*self.ast[1:])
                        self.popStack(r)
                    self.initialCallDepth = initial_call_depth
                    self.stackPointer += 1
                    continue
                this = self.ast[self.stackPointer]
                if isinstance(this, SyntaxSymbol):
                    this = this.toObject(self.cenv)
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
                    self.initialCallDepth = initial_call_depth
                    if r is None:
                        continue
                    if isinstance(r, SyntaxSymbol):
                        self.popStack(r)
                    elif not isinstance(r, list):
                        r1 = [lambda *x: r]
                        # self.ast[:] = r1
                        self.popStack(r1)
                    else:
                        self.ast[:] = r
                    continue
                if isinstance(this, Symbol) and this.isBound(self.cenv):
                    self.ast[self.stackPointer] = this.toObject(self.cenv)
                self.stackPointer += 1
        except Empty as e:
            if hasattr(e, 'ret'):
                return e.ret
            return self.ast[-1]


processer = Processer()
