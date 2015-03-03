from scheme.symbol import Symbol


__author__ = 'perkins'

from scheme.macro import Macro
from scheme.Globals import Globals
from zope.interface import implements


class switch(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        if isinstance(params[0], list):
            key = processer.process([params[0]], processer.cenv)
        else:
            key = params[0].toObject(processer.cenv)
        clauses = params[1:]
        ret = []
        begun = False
        for clause in clauses:
            if clause[0] == 'else':
                begun = True
            if begun:
                if clause[-1] == 'break':
                    ret.extend(clause[1:-1])
                    break;
                ret.extend(clause[1:])
            else:
                if isinstance(clause[0], list):
                    val = processer.process([clause[0]], processer.cenv)
                else:
                    val = clause[0].toObject(processer.cenv)
                if key == val or (isinstance(val, list) and key in val):
                    begun = True
                    if clause[-1] == 'break':
                        ret.extend(clause[1:-1])
                        break;
                    ret.extend(clause[1:])
        return [Symbol('begin')] + ret


class case(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        if isinstance(params[0], list):
            key = processer.process([params[0]], processer.cenv)
        else:
            key = params[0].toObject(processer.cenv)
        clauses = params[1:]
        ret = []
        for clause in clauses:
            if clause[0] == 'else':
                ret.extend(clause[1:])
            else:
                if isinstance(clause[0], list):
                    val = processer.process([clause[0]], processer.cenv)
                else:
                    val = clause[0].toObject(processer.cenv)
                if key == val or (isinstance(val, list) and key in val):
                    ret.extend(clause[1:])
                    break;
        return [Symbol('begin')] + ret


Globals['switch'] = switch()
Globals['case'] = case()