
vm_lx = lambda x:x

VALUE_MAP = {
    float: vm_lx,
    int: vm_lx,
    str: vm_lx,
    dict: id,
    bool: vm_lx,
}

def make_stable_id(unit):
    return VALUE_MAP.get(type(unit), hash)(unit)


def as_ids(*items):
    _id = make_stable_id
    ids = tuple(_id(x) for x in items)
    return ids

