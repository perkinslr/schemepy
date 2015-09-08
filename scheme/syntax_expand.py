from macro import Macro
from zope.interface import providedBy
from macro import Symbol
from scheme.macro import SimpleMacro
from scheme.define_syntax import DefinedSyntax
import scheme
def syntax_expand(processer, params):
    if not isinstance(params, list) or not params:
        return params
    o=[]
    first=params[0]
    if Macro in providedBy(first) or (isinstance(first, Symbol) and first.isBound(processer.env) and Macro in providedBy(first.toObject(processer.env))):
        processer.pushStack(params)
        if Macro not in providedBy(first):
            first = first.toObject(processer.env)
        if isinstance(first, (SimpleMacro, DefinedSyntax)):
            params = first(processer, params[1:])
        
            params = processer.ast[-1]
            return params
            x = syntax_expand(processer, params)
            return x
    for i in params:
        if isinstance(i, list):
            o.append(syntax_expand(processer, i))
        else:
            o.append(i)
    return o



def expandObj(obj):
    processer = scheme.processer.Processer()
    processer.dumpStack()
    processer.ast=[None]
    ast = obj.ast[1]
    syn = syntax_expand(processer, ast)
    while syn!=ast:
        ast=syn
        processer.dumpStack()
        processer.ast=[None]
        syn = syntax_expand(processer, ast)
    obj.ast[1]=syn
    return syn
