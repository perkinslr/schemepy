# noinspection PyTypeChecker
from scheme.debug import DEBUG


class Environment(dict):
    def __init__(self, parent, *args, **kw):
        """

        :rtype : Environment
        """
        self.parent = parent
        dict.__init__(self, *args, **kw)
    def __call__(self, item):
        return self[item]
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)