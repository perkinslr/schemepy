import cStringIO
import parser

import processer

p=processer.processer

def Eval(obj):
    if isinstance(obj, (str, unicode)):
        obj = cStringIO.StringIO(obj)
    ast = parser.Parser(obj).ast
    return p.process(ast)
