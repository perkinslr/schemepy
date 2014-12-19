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
                retval = processer.__class__(processer).process([qq_target], env)
                return retval, False
            if last_idx == 0 and lst.isBound(Globals) and isinstance(lst.toObject(Globals), unquote_splicing):
                qq_target = last_lst.pop(last_idx + 1)
                retval = processer.__class__(processer).process([qq_target], env)
                o_stack.extend(retval)
                return retval, 2
            if lst == ',@':
                qq_target = last_lst.pop(last_idx + 1)

                retval = processer.__class__(processer).process([qq_target], env)
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
    return lst
