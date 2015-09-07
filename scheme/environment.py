# noinspection PyTypeChecker

import debug

class Environment(dict):
    def __init__(self, parent, *args, **kw):
        """

        :rtype : Environment
        """
        self.parent = parent
        super(Environment, self).__init__(*args, **kw)
    def __call__(self, item):
        return self[item]
    def __setitem__(self, key, value):
        if isinstance(key, (list, tuple)):
            if len(key)==1:
                self[key[0]]=value
                return
            print key, value
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
    def __getitem__(self, item):
        if self.parent is not None:
            return super(Environment, self).__getitem__(item) if item in self else self.parent.__getitem__(item)
        return super(Environment, self).__getitem__(item)


ses=[]

class SyntaxEnvironment(dict):
    def __init__(self, *args, **kw):
        if debug.debug_settings['syntax']:
            ses.append(self)
        super(SyntaxEnvironment, self).__init__(*args, **kw)
        self.env=self
    parent = None
    def walk(self, pairs=False):
        items = self.iteritems()
        for key, value in items:
            if pairs:
                yield key, value
            else:
                yield key
            if isinstance(value, SyntaxEnvironment):
                for i in value.walk(pairs):
                    yield i
            elif isinstance(value, list):
                for i in value:
                    if isinstance(i, SyntaxEnvironment):
                        for a in i.walk(pairs):
                            yield a
    def __contains__(self, item):
        for i in self.walk():
            if i == item:
                return True
        return False
    def get_all(self, item):
        if isinstance(item, list):
            o = []
            for i in item:
                o.append(self.get_all(i))
            return zip(*o)
        l = list(self.iget_all(item))
        #if len(l) == 1:
        #    return l[0]
        return l
    def iget_all(self, item):
        for i, v in self.walk(pairs=True):
            if i == item:
                yield v
    def __getitem__(self, item):
        o = []
        found = False
        for i, v in self.walk(pairs=True):
            if i == item:
                found = True
                if i.ellipsis:
                    o.extend(v)
                else:
                    o.append(v)
                #return v
        return o
    def __setitem__(self, item, value):
        from scheme.PatternMatcher import PatternMatcher
        if isinstance(item, PatternMatcher):
            item.setValue(value)
        super(SyntaxEnvironment, self).__setitem__(item, value)
