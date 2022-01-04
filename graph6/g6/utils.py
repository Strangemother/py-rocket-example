
def make_stable_id(unit):

    lx = lambda x:x

    value_map = {
        type(0): lx,
        type(''): lx,
        type({}): id,
        type(True): lx,
    }

    return value_map.get(type(unit), hash)(unit)


def as_ids(*items):
    _id = make_stable_id
    ids = tuple(_id(x) for x in items)
    return ids

