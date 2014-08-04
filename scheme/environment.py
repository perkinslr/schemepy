# noinspection PyTypeChecker
class Environment(dict):
    def __init__(self, parent, *args, **kw):
        """

        :rtype : Environment
        """
        self.parent = parent
        dict.__init__(self, *args, **kw)
    def __call__(self, item):
        return self[item]
