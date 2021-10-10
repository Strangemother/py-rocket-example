"""
Power dependency Chain

A Graph upwards or downward from a given node, forever resolving, computing and
chaining changes to the internal values.

As the graph computes, A change will manifest an event. The event
propagates the allocated direction until the graph fails.

Two chain events act upon a change. the "tap" runs in-line with the change,
altering the value for the first phase event bubbling. Next step accepts the
changed value, emiting a change event.



## Condition

A condition waits for change events for a key. When a change occurs for the
given key the event condition _fires_, setting the condition _key_ to an int.

Given the condition is true the handler function executes.
This allows _complex_ key handling with lighter condition states


Condition: One (egg='foo', bacon=4, cheese=UNDEFINED) -> handler()

    0   egg == 'one'
    1   bacon == 4
    0   cheese != UNDEFINED

One.set(egg, 'one')
One.set(cheese, False)

    1   egg == 'one'
    1   bacon == 4
    1   cheese != UNDEFINED

Condition.set_true() -> execute handler()
"""
from collections import UserDict

def main():
    return test_one()


def test_one():
    target = dict(one=1, two=2, three=3)
    cond = Condition(target)
    # cond.set('egg',4)
    cond.set('one',1)
    cond.set('two',2)
    cond.three = 3
    assert cond.met == True
    cond.three = 2
    assert cond.met == False
    cond.egg = 2
    assert len(cond.table) == len(target)



    print('\n\tTests passed.\n')

    return cond


class Condition(object):

    target = None
    data = None
    # table = None
    met = False
    live = False
    store = False

    def __init__(self, target, data=None, table=None):
        self.target = target
        self.data = data or {}
        # set zeros
        self.met = False
        self.table = table or {x:0 for x in target} # = [0] * len(target)
        self.go_live()

    def go_live(self):
        self.live = True

    def update(self, *dicts, **kwargs):
        r = {}
        ad = dicts + (kwargs,)
        for d in ad:
            r.update(d)

        for k, v in r.items():
            self.safe_set(k, v, check=False)
        self.self_assert()

    def __setattr__(self, k, v):
        if self.live_set(k, v) is None:
            object.__setattr__(self, k, v)

    def live_set(self, k, v, check=True):
        if self.live:
            return self.safe_set(k, v)

    def safe_set(self, k, v, check=True):
        if k in self.table:
            return self.set(k, v)

    def set(self, k, v, check=True):
        # print(k,v)
        match =  int(self.target.get(k) == v)
        # e = Event(key=k, match=match)
        currently_state = self.table[k]
        self.table[k] = match
        if self.store is True:
            self.data[k] = v
            # e.store = True
            # e.value = v
        if match != currently_state:
            # A positive or neg change occured.
            self.emit_key_change(k, currently_state, match)
        valid = self.self_assert()
        # e.met = valid
        return valid

    def self_assert(self):
        met = self.test()
        if met != self.met:
            self.emit_wide_change(met == True)
        self.met = met
        return met

    def emit_key_change(self, key, value, match):
        """A single key change
        """
        print('Key change', key, value, 'valid', match)

    def emit_wide_change(self, complete_match=False):
        if complete_match:
            return self.emit_match_all()
        return self.emit_match_fail()

    def emit_match_all(self):
        print('Condition met', self.table)

    def emit_match_fail(self):
        print('Condition fail', self.table)

    def test(self, table=None):
        sv = set((table or self.table).values())
        # A set of one items with a value of 1
        return len(sv) == 1 and (tuple(sv)[0] == 1)

    def __eq__(self, other):
        if isinstance(other, bool):
            return self.met == other
        return object.__eq__(self, other)

"""Condition Monitor ValueTap

A Condition key can map to another condition key property, applying the
dependency through immediate or event mode.

    ConditionTap
        From Condition A Key
        To   Condition B Key

    B.key == A.key

When A changes, the _taps_ are tested and pushed.
"""
class Event(object):
    store = False
    value = None
    key = None
    match = False
    met = False

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

if __name__ == '__main__':
    c = main()
    print(f'Condition == "c" == {c}')
