from __future__ import division

import sys
import math
import cmath
import operator as op
from zope.interface import providedBy
from scheme import debug
from scheme.Globals import Globals
from scheme.procedure import Procedure

conts=[None]
def setcont(cont):
    conts[0]=cont
    return 1

def getcont():
    return conts[0]

def setDebug(b):
    debug.DEBUG=b

cons = lambda x, y: [x] + y

is_pair = lambda x: x != [] and isa(x, list)

isa = isinstance

def throw(e):
    raise e

def last(o):
    if o:
        return o[-1]

def add_globals(self):
    """Add some Scheme standard procedures."""
    import scheme.eval
    self.update(vars(math))
    self.update(vars(cmath))
    self.update({
        'getcont':getcont,
        'setcont':setcont,
        '%':op.mod,
        'procedure?':lambda x:Procedure in providedBy(x),
        'set-debug':setDebug,
        'throw': throw,
        'Exception': Exception,
        'type': lambda x: type(x),
        '**': op.pow,
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.itruediv, 'not': op.not_,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'equal?': op.eq, 'eq?': op.is_, 'length': len, 'cons': cons,
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'append': op.add,
        'list': lambda *x: list(x), 'list?': lambda x: isa(x, list),
        'null?': lambda x: x == [],
        'boolean?': lambda x: isa(x, bool), 'pair?': is_pair,
        'port?': lambda x: isa(x, file), 'apply': lambda proc, l: proc(*l),
        'len?':len,
        'map':map,
        'in': lambda x,y:x in y,
        'open-input-file': open, 'close-input-port': lambda p: p.file.close(),
        'open-output-file': lambda f: open(f, 'w'), 'close-output-port': lambda p: p.close(),
        'bool':bool,
        'eval':scheme.eval.Exec,
        'last':last,
        'display': lambda x, port=sys.stdout: port.write(x.replace('~n', '\n') if isa(x, (str, unicode)) else str(x))})
    from repl import repl
    repl(open(__file__.rsplit('/',1)[0]+'/builtins.scm'),'',None)
    return self


add_globals(Globals)
