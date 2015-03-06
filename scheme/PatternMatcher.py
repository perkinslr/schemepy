from __future__ import division, unicode_literals
from scheme.environment import SyntaxEnvironment
import scheme.debug

__author__ = 'perkins'

O=[]

class PatternMatcher(object):
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
                        move_on = yield PatternMatcher(i, self.literals, False, True)
                        if move_on:
                            yield "OK"
                            self.idx, i = ei_pattern.next()
                            break
                else:
                    yield PatternMatcher(i, self.literals)
            elif i == '.':
                self.idx, i = ei_pattern.next()
                if isinstance(i, list):
                    raise SyntaxError(". must be followed by a name")
                yield PatternMatcher(i, self.literals, True)
            elif len(self.pattern) > self.idx + 1 and self.pattern[self.idx + 1] == '...':
                yield PatternMatcher(i, self.literals, False, True)
                self.idx, i = ei_pattern.next()
            else:
                yield PatternMatcher(i, self.literals)
    def match(self, params):
        try:
            return self.__match([params])
        except SyntaxError:
            pass
        except TypeError:
            pass
        except AttributeError:
            pass
        if scheme.debug.DEBUG > 1:
            import traceback
            traceback.print_exc()
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
        o = SyntaxEnvironment()
        O.append(o)
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
                params.pop()
                params.pop()
                return o
            else:
                if not params:
                    '''
                    We need a symbol or a list
                    '''
                    raise SyntaxError()
                if self.pattern in self.literals:
                    if params[0] != self.pattern:
                        raise SyntaxError()
                    return SyntaxEnvironment()
                if isinstance(params, list):
                    r = SyntaxEnvironment({self: params[0]})
                    return r
                else:
                    return SyntaxEnvironment({self: params})
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
                    rpm = PatternMatcher(reversed_pattern, self.literals)
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
                        l = [params.pop(0), params]
                        r = patternElement.__match(l)
                        if not l:
                            params = []
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
                raise SyntaxError()
            return o
