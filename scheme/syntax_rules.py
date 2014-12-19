from __future__ import unicode_literals

from zope.interface import implements, classProvides

from scheme.macro import Macro
from scheme.symbol import Symbol
from scheme.environment import Environment

# from scheme.utils import syntax_copy_with_replacement


class SyntaxEnvironment(dict):
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
        if len(l) == 1:
            return l[0]
        return l
    def iget_all(self, item):
        for i, v in self.walk(pairs=True):
            if i == item:
                yield v
    def __getitem__(self, item):
        for i, v in self.walk(pairs=True):
            if i == item:
                return v
        raise IndexError()
    def __setitem__(self, item, value):
        if isinstance(item, patternMatcher):
            item.setValue(value)
        super(SyntaxEnvironment, self).__setitem__(item, value)


# noinspection PyAttributeOutsideInit
class SyntaxSymbol(Symbol):
    def setSyntax(self, transformer):
        self.transformer = transformer
        return self
    def setSymbol(self, symbol):
        self.symbol = symbol
        return self
    def toObject(self, env):
        try:
            possibleEnv = Symbol.getEnv(self, env)
        except NameError:
            possibleEnv = None
        if possibleEnv:
            keys = possibleEnv.keys()
            if self in keys:
                possibleSymbol = keys[keys.index(self)]
                if isinstance(possibleSymbol, SyntaxSymbol) and possibleSymbol.transformer == self.transformer:
                    return possibleEnv[self]
        if not isinstance(self.symbol, Symbol):
            return self.symbol
        return self.symbol.toObject(self.env)
    def getEnv(self, env):
        return self.symbol.getEnv(self.env)
    def setEnv(self, env):
        self.env = env
        return self
    def __repr__(self):
        return "<SyntaxSymbol %s>" % Symbol.__repr__(self)


def transformCode(code, bindings, env, transformer):
    """
    Recursive function to build the transformed code
    :param code: code to transform
    :param bindings:  Environment which details which symbols should not be looked up in the macro's environment
    :param env: Environment to store macro-variables and to use for macro-variable lookup
    :param transformer: the transformer for which the SyntaxSymbols are generated
    :return: transformed code
    """
    o = []
    iterCode = iter(enumerate(code))
    print 101, code
    for idx, i in iterCode:
        print 103, i, o
        if len(code) > idx + 1 and code[idx + 1] == '...':
            iterCode.next()
            o.extend(transformCode(list(bindings.get_all(i)), bindings, env, transformer))
            continue
        if i == '.':
            idx_p1, i_p1 = iterCode.next()
            o_p1 = transformCode(code[idx_p1].toObject(bindings), bindings, env, transformer)
            o.extend(o_p1)
            continue
        if isinstance(i, (list, tuple)):
            print 114, len(o), i
            o.append(transformCode(i, bindings, env, transformer))
        else:
            print 117, len(o)
            if i not in bindings:
                o.append(SyntaxSymbol(i).setEnv(env).setSymbol(Symbol(i)).setSyntax(transformer))
            else:
                o.append(bindings[i])
                # if i == '...' and code[idx-1] in bindings:
                # o.pop(-1)
                # o.pop(-1)
                # o.extend(bindings[code[idx - 1]])
    print 126, o
    return o


class EmptyParams(SyntaxError):
    pass


pd = False


# noinspection PyUnresolvedReferences
class patternMatcher(object):
    def __eq__(self, other):
        """

        :param other: One of ['.' sym] [sym '...'] [sym]
        :return: boolean
        """
        return self.pattern == other
    def setValue(self, val):
        self.value = val
        return self
    def __repr__(self):
        return '<pattern %s (%s) .=%r ...=%r>' % (self.pattern, self.literals, self.dot, self.ellipsis)
    def __init__(self, pattern, literals, dot=False, ellipsis=False):
        self.pattern = pattern
        self.literals = literals
        self.ellipsis = ellipsis
        self.dot = dot
        self.idx = 0
        self.value = None
    def __iter__(self):
        ei_pattern = enumerate(iter(self.pattern))
        for self.idx, i in ei_pattern:
            if isinstance(i, list):
                if len(self.pattern) > self.idx + 1 and self.pattern[self.idx + 1] == '...':
                    while True:
                        move_on = yield patternMatcher(i, self.literals, False, True)
                        if move_on:
                            yield "OK"
                            self.idx, i = ei_pattern.next()
                            break
                else:
                    yield patternMatcher(i, self.literals)
            elif i == '.':
                self.idx, i = ei_pattern.next()
                if isinstance(i, list):
                    raise SyntaxError(". must be followed by a name")
                yield patternMatcher(i, self.literals, True)
            elif len(self.pattern) > self.idx + 1 and self.pattern[self.idx + 1] == '...':
                yield patternMatcher(i, self.literals, False, True)
                self.idx, i = ei_pattern.next()
            else:
                yield patternMatcher(i, self.literals)
    def match(self, params):
        import traceback
        try:
            return self.__match([params])
        except SyntaxError:
            traceback.print_exc()
            return None
        except TypeError:
            traceback.print_exc()
            return None
        except AttributeError:
            traceback.print_exc()
            return None
    def __match(self, params):
        """
        Literals match literals
        Lists match lists (recursive invocation)
        Pattern tokens match lists or symbols
        ... makes the previous element match 0 or more times
        ... continues to consume elements from pattern until a non-matching param is encountered
        . makes the following element consume all following params
        :param params: [Symbol]
        :return: dictionary of pattern variables or False if not a matching pattern
        """
        print 196, self.pattern, params
        o = SyntaxEnvironment()
        if not isinstance(self.pattern, list):  # we're a single element
            if self.dot:
                if not params:
                    o[self] = []
                else:
                    o[self] = [params[0]] + params[1]
                    params.pop()
                    params.pop()
                return o
            elif self.ellipsis:
                o[self] = [params[0]] + params[1]
                return o
            else:
                if not params:
                    '''
                    We need a symbol or a list
                    '''
                    raise EmptyParams()
                if self.pattern in self.literals:
                    if params[0] != self.pattern:
                        raise SyntaxError()
                    return SyntaxEnvironment()
                return SyntaxEnvironment({self: params[0]})
        else:
            if not params:
                raise SyntaxError()
            params = params[0][:]
            ipattern = iter(self)
            for patternElement in ipattern:
                if patternElement.ellipsis:
                    # This element needs to match 0+ sub-elements of params (non-greedy),
                    # so we work backward from the right till this is the last sub-pattern
                    reversed_pattern = self.pattern[self.idx + 2:]
                    rpm = patternMatcher(reversed_pattern, self.literals)
                    reversed_pattern = list(rpm)
                    reversed_pattern.reverse()
                    for rpatternElement in reversed_pattern:
                        if rpatternElement.ellipsis:
                            raise SyntaxError()
                        if rpatternElement.dot:
                            o[rpatternElement] = []
                            continue
                        if params:
                            paramElement = [params.pop(-1)]
                        else:
                            paramElement = []
                        v = rpatternElement.__match(paramElement)
                        o.update(v)
                    # We've matched all the params to the right
                    # without error, whatever's left is given to this pattern
                    if not params:
                        o.update({patternElement: params})
                        try:
                            x = ipattern.send(1)
                        except StopIteration:
                            x = 'OK'
                        if x != 'OK':
                            print 258, x
                            raise SyntaxError(x)
                        break
                    if isinstance(patternElement.pattern, list):
                        matches = []
                        while True:
                            if params:
                                lastParam = False
                                paramElement = [params.pop(0)]
                            else:
                                lastParam = True
                                paramElement = []
                            try:
                                matches.append(patternElement.__match(paramElement))
                            except SyntaxError:
                                if not lastParam:
                                    params.insert(0, paramElement)
                                try:
                                    ipattern.send(True)
                                except StopIteration:
                                    break
                                break;

                        o.update({patternElement: matches})
                        break;
                    else:
                        r = patternElement.__match([params.pop(0), params])
                        o.update(r)
                        break
                if params:
                    if isinstance(params, list):
                        paramElement = [params.pop(0), params]
                    else:
                        paramElement=[params]
                        params=[]
                else:
                    paramElement = []
                o.update(patternElement.__match(paramElement))
                if not paramElement:
                    params = []
            if params:
                print params
                raise SyntaxError()
            return o


class syntax_rules(object):
    implements(Macro)
    classProvides(Macro)
    def __init__(self, processer, ast):
        literals = ast[0]
        patterns = ast[1:]
        self.name = patterns[0][0][0]
        self.env = processer.cenv.parent
        self.literals = literals
        self.patterns = patterns
    def __call__(self, processer, params):
        for pattern in self.patterns:
            template = pattern[1:]
            print 323, len(template)
            pattern = pattern[0][1:]
            bindings = patternMatcher(pattern, self.literals).match(params)
            if bindings is None:
                print 313
                continue
            print 314, bindings
            env = Environment(self.env)

            transformedCode = transformCode(template, bindings, env, self)[0]
            print 327, template
            print 328, transformedCode
            osp = processer.stackPointer
            print 336, osp
            processer.popStack(transformedCode)
            #processer.ast = transformedCode
            processer.stackPointer = osp
            return

        raise SyntaxError("syntax-rules no case matching %r for %s" % (params, self.name))


import scheme.Globals


scheme.Globals.Globals['syntax-rules'] = syntax_rules
