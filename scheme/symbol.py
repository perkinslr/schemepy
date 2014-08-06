from scheme import debug
from scheme.Globals import Globals


class Symbol(unicode):
    def toObject(self, env):
        while env is not None:
            if unicode(self) in env:
                return env[self]
            env = env.parent
        if self.lstrip('-').isdigit():
            return int(self)
        if self.replace('-','').replace('.', '').replace('e','').isdigit():
            return float(self)
        if self[0] == self[-1] == '"':
            return self[1:-1]
        if self == '#t':
            return True
        if self == '#f':
            return False
        try:
            return complex(self.replace('i','j',1))
        except:
            raise NameError(u"Symbol '%s' undefined" % self)
    def isBound(self, env):
        try:
            self.toObject(env)
            return True
        except NameError:
            return False
    def getEnv(self, env):
        while env is not None:
            if unicode(self) in env:
                return env
            env = env.parent
        if self.lstrip('-').isdigit() or self.lstrip('-').replace('.', '').isdigit() or self[0] == self[-1] == '"' or \
                        self == '#t' or self == '#f':
            return Globals
        raise NameError(u"Symbol '%s' undefined" % self)
    def __repr__(self):
        if debug.DEBUG:
            return '<Symbol %s>' % self
        return str(self)
    def __bool__(self):
        if self.isBound(None):
            return bool(self.toObject(Globals))
        return True
    def __add__(self, other):
        if (isinstance(other, Symbol)):
            return self.toObject(Globals)+other.toObject(Globals)
        return str(self)+other