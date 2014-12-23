from __future__ import division
import os
import sys
import math
import cmath
import operator as op
import scheme
from zope.interface import providedBy
from scheme import debug
from scheme.Globals import Globals
from scheme.macro import Macro
from scheme.procedure import Procedure
import cStringIO

def setDebug(b):
    debug.DEBUG = b


cons = lambda x, y: [x] + y

is_pair = lambda x: x != [] and isa(x, list)

isa = isinstance


def throw(e):
    raise e


def last(o):
    if o:
        return o[-1]


def car(x):
    return x[0]


def schemeApply(callable_, args):
    if Macro in providedBy(callable_) or Procedure in providedBy(callable_):
        return callable_(scheme.processer.current_processer, args)
    return callable_(*args)


def List(*x):
    return list(x)

def add_globals(env):
    """Add some Scheme standard procedures."""
    import scheme.eval
    env.update(vars(math))
    env.update(vars(cmath))
    env.update({
        'open-output-string': lambda: cStringIO.StringIO(),
        'get-output-string': lambda ioObj: ioObj.getvalue(),
        '%': op.mod,
        'procedure?': lambda x: Procedure in providedBy(x),
        'set-debug': setDebug,
        'throw': throw,
        'Exception': Exception,
        'type': lambda x: type(x),
        '**': op.pow,
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.itruediv, 'not': op.not_,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'equal?': op.eq, 'eq?': op.is_, 'length': len, 'cons': cons,
        'car': car,
        'cdr': lambda x: x[1:],
        'append': op.add,
        'list': List, 'list?': lambda x: isa(x, list),
        'null?': lambda x: x == [],
        'boolean?': lambda x: isa(x, bool), 'pair?': is_pair,
        'port?': lambda x: isa(x, file), 'apply': schemeApply,
        'len?': len,
        'map': map,
        'in': lambda x, y: x in y,
        'open-input-file': open, 'close-input-port': lambda p: p.file.close(),
        'open-output-file': lambda f: open(f, 'w'), 'close-output-port': lambda p: p.close(),
        'bool': bool,
        'eval': scheme.eval.Exec,
        'last': last,
        'display': lambda x, port=sys.stdout: port.write(x.replace('~n', '\n') if isa(x, (str, unicode)) else str(x))})
    from repl import repl
    import site
    package_locations = site.getsitepackages()
    installed = False
    for pl in package_locations:
        if __file__.startswith(pl):
            installed = True
            break
    if installed:
        p = os.path.join(sys.prefix,'share','schemepy','stdlib')
    else:
        p = os.path.join(*os.path.split(__file__)[:-2]+('stdlib',))
    for scm in os.listdir(p):
        repl(open(os.path.join(p,scm)), '', None)
    return env


add_globals(Globals)
