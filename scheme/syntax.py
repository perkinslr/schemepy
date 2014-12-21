from __future__ import division, unicode_literals
from Queue import Empty
from scheme.symbol import Symbol
from zope.interface import classProvides, implements, implementer, provider
from scheme.macro import Macro
from scheme.Globals import Globals
__author__ = 'perkins'

# noinspection PyAttributeOutsideInit
@provider(Macro)
class SyntaxSymbol(Symbol):
    def __init__(self, *args):
        self.line=0
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
        try:
            possibleEnv = Symbol.getEnv(self, env)
        except NameError:
            possibleEnv = None
        if possibleEnv:
            keys = possibleEnv.keys()
            if self in keys:
                possibleSymbol = keys[keys.index(self)]
                if isinstance(possibleSymbol, SyntaxSymbol) and possibleSymbol.transformer == self.transformer:
                    return possibleEnv
        return self.symbol.getEnv(self.env)
    def setEnv(self, env):
        self.env = env
        return self
    def __repr__(self):
        return "<SyntaxSymbol %s>" % Symbol.__repr__(self)

@implementer(Macro)
class syntax(object):
    def __init__(self, *args):
        pass
    def __call__(self, processer, template):
        o = SyntaxSymbol(processer, template[0]).setSymbol(template[0])
        return o




Globals['syntax']=syntax()
