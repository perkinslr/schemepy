from scheme.symbol import Symbol


def deepcopy(lst):
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