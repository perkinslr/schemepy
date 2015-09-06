from Queue import Empty
import cStringIO
import parser

import processer
import utils


p = processer.processer


def Eval(obj, quotesExpanded=False, ccc=False):
    if isinstance(obj, (str, unicode)):
        obj = cStringIO.StringIO(obj)
    ast = parser.Parser(obj).ast
    try:
        ret = p.doProcess(ast, quotesExpanded=quotesExpanded, ccc=ccc)
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
