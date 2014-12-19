__author__ = 'perkins'

from scheme.Globals import Globals
from scheme.begin import begin


class unquote_splicing(begin):
    pass


Globals['unquote-splicing'] = unquote_splicing()