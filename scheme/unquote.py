__author__ = 'perkins'

from scheme.Globals import Globals
from scheme.begin import begin


class unquote(begin):
    pass


Globals['unquote'] = unquote()