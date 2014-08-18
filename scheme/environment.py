# noinspection PyTypeChecker
from scheme.debug import DEBUG


class Environment(dict):
    def __init__(self, parent, *args, **kw):
        """

        :rtype : Environment
        """
        self.parent = parent
        if parent is not None:
            if parent.get('children'):
                parent['children'].append(self)
            else:
                parent['children'] = [self]
        dict.__init__(self, *args, **kw)
    def __call__(self, item):
        return self[item]
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)