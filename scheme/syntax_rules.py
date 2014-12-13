from zope.interface import implements, providedBy, classProvides
from scheme.macro import MacroSymbol, Macro
from scheme.symbol import Symbol
from scheme.environment import Environment
from scheme.utils import syntax_copy_with_replacement
class syntax_rules(object):
    implements(Macro)
    classProvides(Macro)
    def __init__(self, processer, ast):
        literals=ast[0]
        patterns=ast[1:]
        self.env=processer.cenv
        self.literals=literals
        self.patterns=patterns
    def __call__(self, processer, params):
        for pattern in self.patterns:
            test = pattern[0][1:]
            code = pattern[1:]
            if '...' in test:
                if len(test)-1 > len(params):
                    print 19
                    continue
                #@TODO support ... in other than tail position in pattern
                if '...' in test[:-1]:
                    print 23
                    continue
            else:
                if len(params)!=len(test):
                    print 27, params, test
                    continue
            skip=False
            env=Environment(self.env)
            for idx, sym in enumerate(test):
                if sym in self.literals:
                    if params[idx]!=sym:
                        skip=True
                        break
                    print 36
                    continue
                if sym == '...':
                    env[sym] = params[idx:]
                    print 40
                    break
                env[sym]=params[idx]
            if skip:
                print 44
                continue
            a = [Symbol('begin')] + syntax_copy_with_replacement(code, self.env, **env)
            print 4648, a
            print 49, env
            processer.pushStackN()
            ret = processer.__class__(processer).process([Symbol('begin')] + syntax_copy_with_replacement(code, self.env, **env), env)
            processer.popStackN()
            print 51, ret
            return [Symbol('quote'), ret[-1]]
        print 48
        raise SyntaxError("syntax-rules no case matching %r" %params)





import scheme.Globals
scheme.Globals.Globals['syntax-rules']=syntax_rules
