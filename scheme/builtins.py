import sys
import math
import cmath
import operator as op

from scheme.Globals import Globals


cons = lambda x, y: [x] + y

is_pair = lambda x: x != [] and isa(x, list)

isa = isinstance
def car(lst):
    print 'x',150, lst
    return lst[0]

def add_globals(self):
    """Add some Scheme standard procedures."""

    self.update(vars(math))
    self.update(vars(cmath))
    self.update({
        'type': type,
        '**': op.pow,
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.div, 'not': op.not_,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'equal?': op.eq, 'eq?': op.is_, 'length': len, 'cons': cons,
        'car': car,
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
        'display': lambda x, port=sys.stdout: port.write(x.replace('~n', '\n') if isa(x, (str, unicode)) else str(x))})
    from repl import repl
    repl(open(__file__.rsplit('/',1)[0]+'/builtins.scm'),'',None)
    return self


add_globals(Globals)
