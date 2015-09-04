from macro import Macro
from zope.interface import providedBy
from macro import Symbol
from scheme.macro import SimpleMacro
from scheme.define_syntax import DefinedSyntax
def syntax_expand(processer, params):
    if not isinstance(params, list):
        return params
    o=[]
    print 8, params
    first=params[0]
    if Macro in providedBy(first) or (isinstance(first, Symbol) and first.isBound(processer.env) and Macro in providedBy(first.toObject(processer.env))):
        print 11, params
        processer.pushStack(params)
        if Macro not in providedBy(first):
            first = first.toObject(processer.env)
        if isinstance(first, (SimpleMacro, DefinedSyntax)):
            params = first(processer, params[1:])
        
            params = processer.ast[-1]
            return params
            x = syntax_expand(processer, params)
            print 13,x
            return x
    print 16
    for i in params:
        if isinstance(i, list):
            o.append(syntax_expand(processer, i))
        else:
            o.append(i)
    return o

