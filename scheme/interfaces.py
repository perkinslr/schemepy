from zope import interface


class Procedure(interface.Interface): 
    def __init__(ast, env):
        """"""

    def __call__(processer, params):
        """"""



class Macro(interface.Interface):
    def __init__(ast, env):
        """"""

    def __call__(processer, params):
        """"""

