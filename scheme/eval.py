from Queue import Empty
import cStringIO
import parser

import processer

p=processer.processer

def Eval(obj):
    if isinstance(obj, (str, unicode)):
        obj = cStringIO.StringIO(obj)
    ast = parser.Parser(obj).ast
    try:
        ret = p._process(ast)
    except Empty as e:
        ret = e.ret
    return ret

def Exec(ast):
    try:
        ret = p._process(ast)
        print 22, ret
    except Empty as e:
        ret = e.ret
    return ret