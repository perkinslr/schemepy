enabled=False
from types import CodeType as code, FunctionType as function
from procedure import SimpleProcedure
from symbol import Symbol

import operator as op


import dis

globals().update(dis.opmap)

basic_ops = {op.add:BINARY_ADD,op.mul:BINARY_MULTIPLY,op.sub:BINARY_SUBTRACT,op.div:BINARY_TRUE_DIVIDE}


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




def analyze(obj, env=None, p=None):
    '''Determines if the jit is capable of rewriting a SimpleProcedure to python bytecode.  Returns some basic information if it can be rewritten'''
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
    c = ast[1]
    argcount = len(params)
    constants = get_constants(c)
    symbols = get_symbols(c)
    names = (symbols - constants).difference(params)
    nlocals = len(names)+len(params)
    flags = 67
    name = 'test'
    firstlineno = 0
    lnotab=""
    varnames = set(params)
    filename='testf'
    return argcount, nlocals, flags, constants, names, varnames, filename, name, firstlineno, lnotab


def write_code(obj, env=None, p=None):
    tmp = analyze(obj, env, p)
    if not tmp:
        return False
    argcount, nlocals, flags, constants, names, varnames, filename, name, firstlineno, lnotab = tmp
    stacksize = 0
    constants=(None,)+tuple(constants)
    names=tuple(names)
    varnames=tuple(varnames)
    func = obj.ast[1][0]
    bytecode = []
    print 75, func
    if func.isBound(obj.env):
        func = func.toObject(obj.env)
    if func in basic_ops:
        for l in obj.ast[1][1:]:
            if l.isBound(obj.env):
                o = l.toObject(obj.env)
            else:
                o = l
            if o in constants:
                print 90
                bytecode.append(LOAD_CONST)
                bytecode.append(constants.index(o))
                bytecode.append(0)
            elif o in varnames:
                print 95
                bytecode.append(LOAD_FAST)
                bytecode.append(varnames.index(o))
                bytecode.append(0)
            else:
                print 100
                bytecode.append(LOAD_GLOBAL)
                bytecode.append(names.index(o))
                bytecode.append(0)
            stacksize+=1
        for i in xrange(len(obj.ast[1])-2):
            bytecode.append(basic_ops[func])
        bytecode.append(RETURN_VALUE)
        c = code(argcount, nlocals, stacksize, flags, str.join('', [chr(i) for i in bytecode]), constants, tuple(str(i) for i in names), tuple(str(i) for i in varnames), filename, name, firstlineno, lnotab)
        return c
    return False


def makeFunction(obj, env=None, p=None):
    c = write_code(obj, env, p)
    if not c:
        return False
    return function(c, obj.env)
