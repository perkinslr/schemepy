import cStringIO
import parser

import processer


def Eval(obj):
    if isinstance(obj, (str, unicode)):
        obj = cStringIO.StringIO(obj)
    ast = parser.Parser(obj).ast
    return processer.Processer().process(ast)
