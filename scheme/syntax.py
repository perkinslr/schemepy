from __future__ import division, unicode_literals
from Queue import Empty
from scheme.symbol import Symbol
from zope.interface import classProvides, implements
from scheme.macro import Macro
from scheme.Globals import Globals
__author__ = 'perkins'

# noinspection PyAttributeOutsideInit
class SyntaxSymbol(Symbol):
    classProvides(Macro)
    def __init__(self, *args):
        if len(args) > 1:
            processer, template = args
            self.setSymbol(template)
            self.setEnv(processer.cenv)
    def __new__(cls, *args):
        template = args[-1]
        return super(SyntaxSymbol, cls).__new__(cls, template)
    def setSyntax(self, transformer):
        self.transformer = transformer
        return self
    def setSymbol(self, symbol):
        self.symbol = symbol
        return self
    def toObject(self, env):
        try:
            possibleEnv = Symbol.getEnv(self, env)
        except NameError:
            possibleEnv = None
        if possibleEnv:
            keys = possibleEnv.keys()
            if self in keys:
                possibleSymbol = keys[keys.index(self)]
                if isinstance(possibleSymbol, SyntaxSymbol) and possibleSymbol.transformer == self.transformer:
                    return possibleEnv[self]
        if not isinstance(self.symbol, Symbol):
            return self.symbol
        return self.symbol.toObject(self.env)
    def getEnv(self, env):
        return self.symbol.getEnv(self.env)
    def setEnv(self, env):
        self.env = env
        return self
    def __repr__(self):
        return "<SyntaxSymbol %s>" % Symbol.__repr__(self)


class syntax(object):
    implements(Macro)
    def __init__(self, *args):
        pass
    def __call__(self, processer, template):
        try:
            processer.popStack(SyntaxSymbol(processer, template).setSymbol(template))
        except Empty:
            processer.ast = [SyntaxSymbol(processer, template).setSymbol(template)]




Globals['syntax']=syntax()