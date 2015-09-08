enabled=False
lambdas_enabled=True
unstable_enabled=False
from types import CodeType as code, FunctionType as function, BuiltinFunctionType
from procedure import SimpleProcedure
from symbol import Symbol
import scheme.debug
import operator as op
import warnings
from scheme.Globals import Globals
import dis
import time
import sys
from procedure import Procedure
from zope.interface import providedBy
from itertools import count
from macro import MacroSymbol
from scheme.environment import Environment
globals().update(dis.opmap)

basic_ops = {op.add:BINARY_ADD,op.mul:BINARY_MULTIPLY,op.sub:BINARY_SUBTRACT,op.itruediv:BINARY_TRUE_DIVIDE}
compare_ops = (op.lt, op.le, op.eq, op.ne, op.gt, op.ge, op.contains, object(), op.is_, object(), object(), object())

labelidx=count()

def lookup_value(v, e):
    if isinstance(v, Symbol):
        if v.isBound(e):
            return v.toObject(e)
        return v
    return e[v]

def isaProcedure(obj):
    return Procedure in providedBy(obj) or isinstance(obj, MacroSymbol)


def get_constants(c, s=None):
    if s is None:
        s=set()
    for i in c:
        if isinstance(i, list):
            get_constants(i,s)
            continue
        if isinstance(i, Symbol):
            if i.isBound({}):
                s.add(i.toObject({}))
            continue
        if isinstance(i, (int,long,str,unicode,float,complex)):
            s.add(i)
    return s

def get_symbols(c, s=None):
    if s is None:
        s=set()
    for i in c:
        if isinstance(i, list):
            get_symbols(i,s)
            continue
        if isinstance(i, Symbol):
            if i.isBound({}):
                s.add(i.toObject({}))
                continue
        s.add(i)
    return s

def get_locals(c, s=None, e=None):
    if s is None:
        s=set()
    if c:
        f = c[0]
        if isinstance(f, Symbol) and f.isBound(e):
            f=f.toObject(e)
        if isinstance(f, scheme.define.define):
            what = c[1]
            if isinstance(what, list):
                return None
            s.add(what)
            return s
    for i in c:
        if isinstance(i, list):
            if get_locals(i,s,e) is None:
                return None
            continue
    return s


def analyze(obj, env=None, p=None):
    '''Determines if the jit may be capable of rewriting a SimpleProcedure to python bytecode.  Returns some basic information if it can be rewritten'''
    if p and env is None:
        env=p.env
    while isinstance(obj, Symbol):
        if not obj.isBound(env):
            return False
        obj=obj.toObject(env)
    if not isinstance(obj, SimpleProcedure):
        return False
    ast = obj.ast
    params=ast[0]
    flags = 67
    c = ast[1:]
    constants = get_constants(c).union()
    symbols = get_symbols(c)
    localnames = get_locals(c,e=obj.env)
    if localnames is None:
        return False
    localnames = localnames.difference(params)
    names = (symbols - constants).difference(params).difference(localnames)
    nlocals = len(params)+len(localnames)
    
    name = str(obj.name)
    firstlineno = obj.lineno or 0
    if not isinstance(params, list):
        flags|=4
        varargs = [params]
        params=[params]
        argcount=len(params)-1
        names.add('list')
    else:
        argcount = len(params)
        varargs = False
    varnames = params+list(localnames)
    filename='<jit>'
    return argcount, nlocals, flags, tuple(constants)+(obj.env,[None]), names, varnames, filename, name, firstlineno, varargs


class Loader(object):
    def __init__(self, constants, varnames, names, env, bytecode, stackptr):
        self.constants = constants
        self.varnames = varnames
        self.names = names
        self.env = env
        self.bytecode = bytecode
        self.nonlocals = []
        self.stackptr = stackptr
    def storeItem(self, item, bytecode=None):
        if bytecode is None:
            bytecode = self.bytecode
        item = str(item)
        idx = self.varnames.index(item)
        bytecode.append(STORE_FAST)
        bytecode.append(idx%256)
        bytecode.append(idx//256)
    def loadExtraConstant(self, o, bytecode=None):
        if bytecode is None:
            bytecode = self.bytecode
        if o in self.constants:
            return self.loadItem(o,bytecode)
        if o not in self.nonlocals:
            self.nonlocals.append(o)
        idx=len(self.constants)+self.nonlocals.index(o)
        bytecode.add(LOAD_CONST,idx%256,idx//256)
    def loadItem(self, o, bytecode=None):
        constants = self.constants
        varnames = self.varnames
        names = self.names
        if bytecode is None:
            bytecode = self.bytecode
        if str(o) in varnames:
            o=str(o)
        elif not isinstance(o, Symbol):
            pass
        elif isinstance(o, MacroSymbol):
            pass
        elif o.isBound({}):
            o = o.toObject({})
        if o in constants:
            idx = constants.index(o)
            bytecode.append(LOAD_CONST)
            bytecode.append(idx%256)
            bytecode.append(idx//256)
        elif o in varnames:
            idx = varnames.index(o)
            bytecode.append(LOAD_FAST)
            bytecode.append(idx%256)
            bytecode.append(idx//256)
        elif o in names:
            if not isinstance(o, Symbol):
                o=names[names.index(o)]
            if o.isBound(Globals) and o.toObject(Globals) is o.toObject(self.env):
                idx = names.index(o)
                bytecode.append(LOAD_GLOBAL)
                bytecode.append(idx%256)
                bytecode.append(idx//256)
            else:
                self.loadItem(lookup_value)
                bytecode.append(LOAD_CONST)
                if o not in self.nonlocals:
                    self.nonlocals.append(o)
                idx = len(self.constants)+self.nonlocals.index(o)
                bytecode.append(idx%256)
                bytecode.append(idx//256)
                self.loadItem(self.env)
                self.stackptr+3
                self.stackptr-3
                bytecode.add(CALL_FUNCTION,2,0)
                #raise ValueError("Trying to load nonlocal value: %r"%o)
        else:
            if isinstance(o, MacroSymbol):
                return self.loadItem(o.toObject({}), bytecode)
            print 156,constants
            print 157,varnames
            print 158,names
            if unstable_enabled:
                print type(o)
                warnings.warn("Trying to load unknown value: %r, assuming constant"%o)
                self.loadExtraConstant(o,bytecode)
            else:
                raise ValueError("Trying to load unknown value: %r"%o)

class label(object):
    def __init__(self, name):
        self.name=name

class goto(object):
    def __init__(self, label):
        self.label=label

class Bytecode(list):
    def __init__(self, lineno=0):
        self.lineno = lineno
        self.opcodeno = 0
        self.lnotab = []
        self.labels = {}
    def add(self, *a):
        for i in a:
            self.append(i)
    def get_lnotab(self):
        return str.join('', [chr(i) for i in self.lnotab])
    def nextLine(self, lineno):
        if self.lineno > lineno:
            return
        oc_offset = len(self) - self.opcodeno
        self.opcodeno = len(self)
        lno_offset = lineno - self.lineno
        self.lineno = lineno
        while oc_offset > 255:
            self.lnotab.append(255)
            self.lnotab.append(0)
            oc_offset -= 255
        while lno_offset > 255:
            lno_offset-=255
            self.lnotab.append(0)
            self.lnotab.append(255)
        self.lnotab.append(oc_offset)
        self.lnotab.append(lno_offset)
    def append(self, value):
        if scheme.debug.debug_settings['jit-one-opcode-per-line']:
            self.nextLine(self.lineno+1)
        if isinstance(value, label):
            self.labels[value.name]=len(self)
            return
        super(Bytecode, self).append(value)
        if isinstance(value, goto):
            self.append(0)
    def flatten(self):
        o=[]
        itr = iter(self)
        for i in itr:
            if isinstance(i, int):
                o.append(chr(i))
            elif isinstance(i, goto):
                itr.next()
                idx = self.labels[i.label]
                o.append(chr(idx%256))
                o.append(chr(idx//256))
        return str.join('', o)

class StackPointer(object):
    def __repr__(self):
        return "<StackPointer %i/%i>"%(self.ptr,self.maxptr)
    def __init__(self):
        self.ptr = 0
        self.maxptr = 0
    def __add__(self, other):
        self.ptr+=other
        if self.ptr > self.maxptr:
            self.maxptr = self.ptr
        return self
    def __sub__(self, other):
        self.ptr-=other
        return self
    def __cmp__(self, other):
        return cmp(self.ptr, other)

def write_code(obj, env=None, p=None):
    tmp = analyze(obj, env, p)
    if not tmp:
        return False
    argcount, nlocals, flags, constants, names, varnames, filename, name, firstlineno, varargs = tmp
    if None in constants:
        constants.remove(None)
    stackptr = StackPointer()
    constants=(None,lookup_value,isaProcedure,scheme.processer.processer)+tuple(constants)
    names=("pushStack",)+tuple(names)
    varnames=list(varnames)
    c = iter(obj.ast[1:])
    bytecode = Bytecode(lineno=obj.lineno or 0)
    loader = Loader(constants, varnames, names, obj.env, bytecode, stackptr)
    def write_nested_code(statement):
        if not isinstance(statement, list):
            if isinstance(statement, Symbol):
                bytecode.nextLine(statement.line)
            stackptr + 1
            loader.loadItem(statement)
            return True
        func = statement[0]
        while isinstance(func, Symbol):
            bytecode.nextLine(func.line)
            if func.isBound(obj.env):
                func = func.toObject(obj.env)
            else:
                break
        if func in basic_ops.keys():
            isp = stackptr.ptr
            for l in statement[1:]:
                if isinstance(l, list):
                    if not write_nested_code(l):
                        return False
                    continue
                stackptr + 1
                loader.loadItem(l)
            while stackptr > isp + 1:
                stackptr - 1
                bytecode.append(basic_ops[func])
            return True
        elif func in compare_ops:
            isp = stackptr.ptr
            istatement = iter(statement[1:])
            lidx = labelidx.next()
            for l in istatement:
                if isinstance(l, list):
                    if not write_nested_code(l):
                        return False
                else:
                    stackptr + 1
                    loader.loadItem(l)
                if stackptr > isp + 1:
                    stackptr + 1
                    if istatement.__length_hint__():
                        bytecode.append(DUP_TOP)
                        bytecode.append(ROT_THREE)
                    bytecode.append(COMPARE_OP)
                    stackptr - 1
                    bytecode.append(compare_ops.index(func))
                    bytecode.append(0)
                    if istatement.__length_hint__():
                        bytecode.append(JUMP_IF_FALSE_OR_POP)
                        bytecode.append(goto('false%i'%lidx))
                        stackptr - 1
                    else:
                        bytecode.append(JUMP_ABSOLUTE)
                        bytecode.append(goto('false%i'%lidx))
            bytecode.append(label('false%i'%lidx))
            bytecode.append(ROT_TWO)
            bytecode.append(POP_TOP)
            stackptr - 1
            bytecode.append(label('false%i'%lidx))
            return True
        elif isinstance(func, (BuiltinFunctionType, function, type)):
            isp = stackptr.ptr
            istatement = iter(statement[1:])
            loader.loadItem(statement[0])
            for l in statement[1:]:
                if isinstance(l, list):
                    if not write_nested_code(l):
                        return False
                    continue
                stackptr + 1
                loader.loadItem(l)
            bytecode.add(CALL_FUNCTION, len(statement[1:]), 0)
            return True
        elif isinstance(func, scheme.define.define):
            var = statement[1]
            if isinstance(var, list):
                return False
            val = statement[2]
            if isinstance(val, list):
                if not write_nested_code(val):
                    return False
            else:
                loader.loadItem(val)
                stackptr +1
            bytecode.add(DUP_TOP)
            bytecode.add(DUP_TOP)
            loader.storeItem(var)
            loader.loadItem(obj.env)
            loader.loadExtraConstant(var)
            bytecode.add(ROT_THREE,ROT_THREE,ROT_TWO)
            bytecode.add(STORE_MAP)
            bytecode.add(POP_TOP)
            return True
        elif isinstance(func, scheme.IF.IF):
            lidx = labelidx.next()
            if not write_nested_code(statement[1]):
                return False
            bytecode.add(JUMP_IF_FALSE_OR_POP, goto('iffalse%i'%lidx))
            if not write_nested_code(statement[2]):
                return False
            bytecode.add(JUMP_ABSOLUTE, goto('end%i'%lidx))
            bytecode.add(label('iffalse%i'%lidx))
            if len(statement)==4:
                bytecode.add(POP_TOP)
                if not write_nested_code(statement[3]):
                    return False
            bytecode.add(label('end%i'%lidx))
            return True
        elif isinstance(func, scheme.begin.begin):
            c = iter(statement[1:])
            isp = stackptr.ptr
            for statement in c:
                while stackptr > isp:
                    bytecode.append(POP_TOP)
                    stackptr-1
                if not isinstance(statement, list):
                    if isinstance(statement, Symbol):
                        bytecode.nextLine(statement.line)
                    stackptr + 1
                    loader.loadItem(statement)
                    if c.__length_hint__() > 0:
                        bytecode.append(POP_TOP)
                        stackptr - 1
                    continue
                if not write_nested_code(statement):
                    return False
            return True
        elif isaProcedure(func):
            ls = len(statement)-1
            loader.loadItem(func)
            if func is not obj:
                loader.loadItem(scheme.processer.processer)
                bytecode.add(DUP_TOP)
                bytecode.add(LOAD_ATTR,names.index("pushStack")%256,names.index("pushStack")//256)
                loader.loadItem([None])
                bytecode.add(CALL_FUNCTION,1,0)
                bytecode.add(POP_TOP)
            for arg in statement[1:]:
                if not write_nested_code(arg):
                    return False
            if func is not obj:
                bytecode.add(BUILD_LIST, ls%256,ls//256)
                bytecode.add(CALL_FUNCTION, 2, 0)
            else:
                bytecode.add(CALL_FUNCTION, ls, 0)
            stackptr-(ls-1)
            return True
        elif isinstance(func, Symbol):
            #not currently resolvable, so we calculate it's value at runtime.  If it's a Procedure or special form, we'll apply it.  Only use these if unstable optimizations enabled
            gidx=labelidx.next()
            if unstable_enabled:
                ls = len(statement)-1
                loader.loadItem(isaProcedure)
                stackptr+1
                loader.loadItem(func)
                stackptr+1
                bytecode.add(DUP_TOP,ROT_THREE,CALL_FUNCTION,1,0)
                bytecode.add(POP_JUMP_IF_TRUE)
                bytecode.add(goto("applyProcedure%i"%gidx))
                #it's a function
                for arg in statement[1:]:
                    if not write_nested_code(arg):
                        return False
                bytecode.add(CALL_FUNCTION, ls, 0)
                stackptr-(ls-1)
                bytecode.add(JUMP_ABSOLUTE, goto("end%i"%gidx))
                bytecode.add(label("applyProcedure%i"%gidx))
                loader.loadItem(scheme.processer.processer)
                for arg in statement[1:]:
                    if not write_nested_code(arg):
                        return False
                bytecode.add(BUILD_LIST,ls%256,ls//256)
                stackptr-(ls-1)
                bytecode.add(CALL_FUNCTION,2,0)
                stackptr-3
                bytecode.add(label('end%i'%gidx))
                
                
                return True
            else:
                return False
        elif isinstance(func, list):
            if not write_nested_code(func):
                return False
            for arg in statement[1:]:
                if not write_nested_code(arg):
                    return False
            bytecode.add(CALL_FUNCTION, len(statement)-1, 0)
            stackptr - (len(statement)-2)
            return True
        elif isinstance(func, scheme.Lambda.Lambda):
            if unstable_enabled and lambdas_enabled:
                p = scheme.processer.processer
                p.pushStackN()
                p.cenv=Environment(p.cenv)
                print 470, 'statically compiling and linking lambda'
                f = func(p, statement[1:]).toObject({})
                try:
                    if isinstance(f, SimpleProcedure):
                        f = makeFunction(f)
                finally:
                    p.popStackN()
                loader.loadExtraConstant(f)
                return True
            return False
        else:
            print type(func)
            return False
    if varargs:
        for vararg in varargs:
            loader.loadItem('list-type')
            loader.loadItem(vararg)
            bytecode.append(CALL_FUNCTION)
            bytecode.append(1)
            bytecode.append(0)
            loader.storeItem(vararg)
    for statement in c:
        while stackptr > 0:
            bytecode.append(POP_TOP)
            stackptr-=1
        if not isinstance(statement, list):
            if isinstance(statement, Symbol):
                bytecode.nextLine(statement.line)
            stackptr + 1
            loader.loadItem(statement)
            if c.__length_hint__() > 0:
                bytecode.append(POP_TOP)
                stackptr -= 1
            continue
        if not write_nested_code(statement):
            return False
    if not bytecode:
        loader.loadItem(None)
    bytecode.append(RETURN_VALUE)
    c = code(argcount, nlocals, stackptr.maxptr, flags, bytecode.flatten(), constants+tuple(loader.nonlocals), tuple(str(i) for i in names), tuple(str(i) for i in varnames), filename, name, firstlineno, bytecode.get_lnotab())
    if scheme.debug.debug_settings['jit']:
        print stackptr
    return c


def makeFunction(obj, env=None, p=None):
    from syntax_expand import expandObj
    if scheme.debug.debug_settings['jit-crash-on-error']:
        expandObj(obj)
        c = write_code(obj, env, p)
    else:
        try:
            expandObj(obj)
            c = write_code(obj, env, p)
        except:
            return obj
    if not c:
        return obj
    if scheme.debug.debug_settings['jit']:
        import dis
        print obj.ast
        dis.dis(c)
    return function(c, p.env if p else Globals)
