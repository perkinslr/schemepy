from __future__ import division, unicode_literals
from scheme.symbol import Symbol
from zope.interface import directlyProvides, implements, providedBy
from scheme.macro import Macro
from scheme.Globals import Globals
from scheme.syntax import SyntaxSymbol
__author__ = 'perkins'


class DefinedSyntax(object):
    implements(Macro)
    def __init__(self, processer, transformer):
        if isinstance(transformer, Symbol):
            transformer=transformer.toObject(processer.cenv)
        self.transformer = transformer
        directlyProvides(transformer, Macro)
    def __call__(self, processer, params):
        syntax_object = SyntaxSymbol([processer.ast[0]] + params).setSymbol([processer.ast[0]] + params)
        osp = processer.stackPointer
        o = self.transformer(processer, [syntax_object])
        if o is not None:
            processer.popStack(o)
        processer.stackPointer = osp


class DefineSyntax(object):
    implements(Macro)
    def __init__(self):
        pass
    def __call__(self, processer, params):
        name = params[0]
        transformer = processer.process([params[1]], processer.cenv)
        processer.cenv.parent[name]=DefinedSyntax(processer, transformer)
        return processer.cenv.parent[name]






Globals['define-syntax']=DefineSyntax()
