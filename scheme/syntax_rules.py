from __future__ import unicode_literals

from zope.interface import implements, classProvides

from scheme.macro import Macro
from scheme.symbol import Symbol
from scheme.environment import Environment, SyntaxEnvironment
from scheme.syntax import SyntaxSymbol
from scheme.PatternMatcher import PatternMatcher
# from scheme.utils import syntax_copy_with_replacement


from scheme.utils import transformCode













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
        params=params[0].toObject(processer.cenv)
        for pattern in self.patterns:
            template = pattern[1:]
            pattern = pattern[0]
            bindings = PatternMatcher(pattern, self.literals).match(params)
            if bindings is None:
                continue
            env = Environment(self.env)
            transformedCode = transformCode(template, bindings, env, self)[0]
            #osp = processer.stackPointer
            #processer.popStack(transformedCode)
            ##processer.ast = transformedCode
            #processer.stackPointer = osp
            return transformedCode
        raise SyntaxError("syntax-rules no case matching %r for %s" % (params, self.name))


import scheme.Globals


scheme.Globals.Globals['syntax-rules'] = syntax_rules
