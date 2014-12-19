# noinspection PyTypeChecker


class Environment(dict):
    def __init__(self, parent, *args, **kw):
        """

        :rtype : Environment
        """
        self.parent = parent
        if parent is not None and type(parent) == Environment:
            if hasattr(parent, 'children'):
                parent.children.append(self)
            else:
                parent.children = [self]
        super(Environment, self).__init__(*args, **kw)
    def __call__(self, item):
        return self[item]
    def __setitem__(self, key, value):
        if isinstance(key, (list, tuple)):
            if len(key) != len(value):
                raise SyntaxError("Setting multiple symbols require the proper number of values")
            for idx, i in enumerate(key):
                self[i] = value[idx]
            return
        dict.__setitem__(self, key, value)
    def __repr__(self):
        import Globals
        if self is Globals.Globals:
            return '{GLOBALS}'
        return '<Environment parent=%r, %s>' % (self.parent, dict.__repr__(self))