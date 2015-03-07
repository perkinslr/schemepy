from __future__ import unicode_literals
from Queue import Empty

from zope.interface import implements, classProvides
from scheme.procedure import Procedure
from scheme.macro import Macro
from scheme.symbol import Symbol
from scheme.environment import Environment, SyntaxEnvironment
from scheme.syntax import SyntaxSymbol
from scheme.PatternMatcher import PatternMatcher
# from scheme.utils import syntax_copy_with_replacement


from scheme.utils import transformCode


class syntax_case(object):
    implements(Macro)
    #classProvides(Macro)
    def __init__(self):
        #literals = ast[0]
        #patterns = ast[1:]
        #self.name = patterns[0][0][0]
        #self.env = processer.cenv.parent
        #self.literals = literals
        #self.patterns = patterns
        pass
    def __call__(self, processer, params):
        e = processer.cenv
        syntax_object = params[0]
        syntax_object = processer.process([syntax_object], e)
        syntax_list = syntax_object.toObject(e)
        while isinstance(syntax_list, SyntaxSymbol):
            syntax_list = syntax_list.toObject(e)
        literals = params[1]
        patterns = params[2:]
        for pattern in patterns:
            if len(pattern) == 2:
                template = pattern[1:]
                pattern = pattern[0]
                guard = True
            else:
                template = pattern[2:]
                guard = pattern[1]
                pattern = pattern[0]
            bindings = PatternMatcher(pattern, literals).match(syntax_list)
            if bindings is None:
                continue
            processer.pushStack([guard])
            icd = processer.callDepth
            r = processer.doProcess([guard], processer.cenv)
            while processer.callDepth > icd:
                processer.popStackN()
            processer.popStack(r)
            if not r:
                continue
            env = Environment(processer.cenv)
            transformedCode = transformCode(template, bindings, env, bindings)
            return transformedCode[0]
        raise SyntaxError("syntax-case no case matching %r" % (syntax_list))


import scheme.Globals


scheme.Globals.Globals['syntax-case'] = syntax_case()

O=[]
