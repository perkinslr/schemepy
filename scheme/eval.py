from Queue import Empty
import cStringIO
import parser

import processer
import utils


p = processer.processer


def Eval(obj):
    if isinstance(obj, (str, unicode)):
        obj = cStringIO.StringIO(obj)
    ast = parser.Parser(obj).ast
    try:
        ret = p.doProcess(ast)
    except Empty as e:
        # noinspection PyUnresolvedReferences
        ret = e.ret
    return ret


def Exec(ast):
    try:
        ret = p.doProcess(utils.deepcopy(ast))
    except Empty as e:
        # noinspection PyUnresolvedReferences
        ret = e.ret
    return ret
