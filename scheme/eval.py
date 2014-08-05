import cStringIO
import parser

import processer

p=processer.processer

def Eval(obj):
    if isinstance(obj, (str, unicode)):
        obj = cStringIO.StringIO(obj)
    ast = parser.Parser(obj).ast
    return p.process(ast)

def Exec(ast):
    #print 15, ast
    ret = p.process(ast)
    #print 17, ret
    return ret