__author__ = 'perkins'


from scheme.macro import Macro, MacroSymbol
from scheme.Globals import Globals
from zope.interface import implements
from utils import copy_with_quasiquote
from scheme.begin import begin

class unquote(begin):
    pass


Globals['unquote'] = unquote()