from scheme.environment import Environment
from scheme.symbol import Symbol


class callCCBounce(Exception):
    pass


def deepcopy(lst):
    if isinstance(lst, dict) and not isinstance(lst, Environment):
        d = {}
        for i in lst:
            d[i] = deepcopy(lst[i])
        return d
    if isinstance(lst, tuple):
        lst = list(lst)
    if not isinstance(lst, list):
        return lst
    o = []
    for i in lst:
        o.append(deepcopy(i))
    return o


def copy_with_replacement(lst, **vals):
    if not isinstance(lst, list):
        if isinstance(lst, Symbol) and lst in vals:
            return vals[lst]
        return lst
    o = []
    for i in lst:
        o.append(copy_with_replacement(i, **vals))
    return o


def copy_with_quote(lst):
    from scheme.macro import MacroSymbol
    if not isinstance(lst, list):
        if isinstance(lst, Symbol):
            if lst.isBound(None):
                return MacroSymbol(lst).setEnv({lst: lst.toObject(None)})
            return MacroSymbol(lst).setEnv({lst: lst})
        return lst
    o = []
    for i in lst:
        o.append(copy_with_quote(i))
    return o

def copy_with_quasisyntax(processer, env, lst, last_lst=None, last_idx=None, o_stack=None):
    from scheme.unquote import unsyntax
    from scheme.unquote_splicing import unsyntax_splicing
    from scheme.macro import MacroSymbol
    from scheme.syntax import SyntaxSymbol
    from scheme.Globals import Globals
    if not isinstance(lst, list):
        if isinstance(lst, Symbol):
            if last_idx == 0 and lst.isBound(Globals) and isinstance(lst.toObject(Globals), unsyntax):
                qq_target = last_lst.pop(last_idx + 1)
                retval = processer.process([qq_target], env)
                return retval, True
            if lst == '#,':
                qq_target = last_lst.pop(last_idx + 1)
                retval = processer.__class__(processer).process([qq_target], env)
                return retval, False
            if last_idx == 0 and lst.isBound(Globals) and isinstance(lst.toObject(Globals), unsyntax_splicing):
                qq_target = last_lst.pop(last_idx + 1)
                retval = processer.__class__(processer).process([qq_target], env)
                o_stack.extend(retval)
                return retval, 2
            if lst == '#,@':
                qq_target = last_lst.pop(last_idx + 1)

                retval = processer.__class__(processer).process([qq_target], env)
                return retval, 3
            return lst, False
            return SyntaxSymbol(lst).setSymbol(lst), False
        return lst, False
    o = []
    o_stack.append(o)
    for idx, i in enumerate(lst):
        r = copy_with_quasisyntax(processer, env, i, lst, idx, o_stack)
        if r[1] == 3:
            o.extend(r[0])
            continue
        if r[1] == 2:
            return r[0], 3
        elif r[1]:
            return r[0], False
        else:
            o.append(r[0])
    return o, False


def copy_with_quasiquote(processer, env, lst, last_lst=None, last_idx=None, o_stack=None):
    from scheme.unquote import unquote
    from scheme.unquote_splicing import unquote_splicing
    from scheme.macro import MacroSymbol
    from scheme.Globals import Globals
    if not isinstance(lst, list):
        if isinstance(lst, Symbol):
            if last_idx == 0 and lst.isBound(Globals) and isinstance(lst.toObject(Globals), unquote):
                qq_target = last_lst.pop(last_idx + 1)
                retval = processer.process([qq_target], env)
                return retval, True
            if lst == ',':
                qq_target = last_lst.pop(last_idx + 1)
                processer.pushStack(qq_target)
                retval = processer.process([qq_target], env)
                processer.popStack(retval, wrap=False)
                return retval, False
            if last_idx == 0 and lst.isBound(Globals) and isinstance(lst.toObject(Globals), unquote_splicing):
                qq_target = last_lst.pop(last_idx + 1)
                processer.pushStack(qq_target)
                retval = processer.process([qq_target], env)
                processer.popStack(retval, wrap=False)
                o_stack.extend(retval)
                return retval, 2
            if lst == ',@':
                qq_target = last_lst.pop(last_idx + 1)
                processer.pushStack(qq_target)
                retval = processer.process([qq_target], env)
                processer.popStack(retval, wrap=False)
                return retval, 3
            return MacroSymbol(lst).setEnv({lst: lst}), False
        return lst, False
    o = []
    o_stack.append(o)
    for idx, i in enumerate(lst):
        r = copy_with_quasiquote(processer, env, i, lst, idx, o_stack)
        if r[1] == 3:
            o.extend(r[0])
            continue
        if r[1] == 2:
            return r[0], 3
        elif r[1]:
            return r[0], False
        else:
            o.append(r[0])
    return o, False


def symbols_to_values(lst, env):
    if not isinstance(lst, list):
        if isinstance(lst, Symbol):
            return lst.toObject(env)
        return lst
    o = []
    for i in lst:
        o.append(symbols_to_values(i, env))
    return o


def expand_syntax(lst):
    for idx, this in enumerate(lst):
        if this == "#'":
            quoteTarget = lst.pop(idx + 1)
            if quoteTarget == "#'":
                def getQuoteTarget():
                    qt = lst.pop(idx + 1)
                    if qt == "#'":
                        return [Symbol('syntax'), getQuoteTarget()]
                    return qt
                quoteTarget = [Symbol('syntax'), getQuoteTarget()]
            lst[idx] = [Symbol('syntax'), quoteTarget]
        elif this == "#`":
            quoteTarget = lst.pop(idx + 1)
            if quoteTarget == "#`":
                def getQuoteTarget():
                    qt = lst.pop(idx + 1)
                    if qt == "`":
                        return [Symbol('quasisyntax'), getQuoteTarget()]
                    return qt
                quoteTarget = [Symbol('quasisyntax'), getQuoteTarget()]
            lst[idx] = [Symbol('quasisyntax'), quoteTarget]
        elif isinstance(this, list):
            expand_quotes(this)
    return lst



def expand_quotes(lst):
    for idx, this in enumerate(lst):
        if this == "'":
            quoteTarget = lst.pop(idx + 1)
            if quoteTarget == "'":
                def getQuoteTarget():
                    qt = lst.pop(idx + 1)
                    if qt == "'":
                        return [Symbol('quote'), getQuoteTarget()]
                    return qt
                quoteTarget = [Symbol('quote'), getQuoteTarget()]
            lst[idx] = [Symbol('quote'), quoteTarget]
        elif this == "`":
            quoteTarget = lst.pop(idx + 1)
            if quoteTarget == "`":
                def getQuoteTarget():
                    qt = lst.pop(idx + 1)
                    if qt == "`":
                        return [Symbol('quasiquote'), getQuoteTarget()]
                    return qt
                quoteTarget = [Symbol('quasiquote'), getQuoteTarget()]
            lst[idx] = [Symbol('quasiquote'), quoteTarget]
        elif isinstance(this, list):
            expand_quotes(this)
    return expand_syntax(lst)


def getUniqueSymbol(c):
    import time, hashlib
    return Symbol(str(c) + hashlib.md5(str(time.time())).hexdigest())

B=[]

def transformCode(code, bindings, env, transformer, localSymbols = None):
    """
    Recursive function to build the transformed code
    :param code: code to transform
    :param bindings:  Environment which details which symbols should not be looked up in the macro's environment
    :param env: Environment to store macro-variables and to use for macro-variable lookup
    :param transformer: the transformer for which the SyntaxSymbols are generated
    :return: transformed code
    """
#    B.append(bindings)
    from scheme.macro import MacroSymbol
    if localSymbols is None:
        localSymbols = {}
    if not isinstance(code, list):
        if code in bindings:
            return bindings[code]
        try:
            code.toObject(env)
            return MacroSymbol(code).setEnv(env)
        except:
            pass
        if code not in localSymbols:
                localSymbols[code]=getUniqueSymbol(code)
        return localSymbols[code]
    o=[]
    itercode=iter(enumerate(code))
    for idx, c in itercode:
        if isinstance(c, list):
            newC=transformCode(c, bindings, env, transformer, localSymbols)
            o.append(newC)
        else:
            if len(code) > idx + 1 and code[idx+1]=='...':
                itercode.next()
                tmp = bindings[c]#.get_all(c)
                #if isinstance(tmp, list):
                o.extend(tmp)
                #else:
                #    o.append(tmp)
                continue
            if c in bindings:
                #o.append(bindings.get_all(c))
                o.extend(bindings[c])
                continue
            try:
                c.toObject(env)
                o.append(MacroSymbol(c).setEnv(env))
                continue
            except Exception as e:
                #print e
                pass
            if c not in localSymbols:
                localSymbols[c]=getUniqueSymbol(c)
            o.append(localSymbols[c])
    return o
 
