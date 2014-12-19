from zope import interface


# noinspection PyMethodParameters,PyUnusedLocal
class Procedure(interface.Interface):
    def __init__(ast, env):
        """"""

    def __call__(processer, params):
        """"""


# noinspection PyMethodParameters,PyUnusedLocal
class Macro(interface.Interface):
    def __init__(ast, env):
        """"""

    def __call__(processer, params):
        """"""

