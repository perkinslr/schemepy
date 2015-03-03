__author__ = 'perkins'

from scheme.Globals import Globals
from scheme.begin import begin


class unquote_splicing(begin):
    pass

class unsyntax_splicing(begin):
    pass


Globals['unquote-splicing'] = unquote_splicing()
Globals['unsyntax-splicing'] = unsyntax_splicing()
