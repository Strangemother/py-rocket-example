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
# from collections import UserDict
from functools import partial


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


def assign_as_property(instance, prop_name, *a):
    """Attach prop_fn to instance with name prop_name.
    Assumes that prop_fn takes self as an argument.
    Reference: https://stackoverflow.com/a/1355444/509706
    """
    class_name = instance.__class__.__name__
    pr = property(*a)
    body = {prop_name: pr}
    child_class = type(class_name, (instance.__class__,), body)

    instance.__class__ = child_class
    return pr


class ConditionProps(object):
    """Implement a condition and its attributes on this parent
    unit through property methods
    """
    condition_target = None

    def __init__(self):
        self.build_condition(bind=self)

    def get_condition_target(self):
        return dict(self.condition_target or {})

    def build_condition(self, bind=None):
        target = self.get_condition_target()
        print('Target', target)
        cond = Condition(target, bind=bind)
        self._condition = cond
        props = {}
        for name in target:
            # property(fget=None, fset=None, fdel=None, doc=None) -> property
            fget = partial(self._condition_get, name)
            fset = partial(self._condition_set, name)
            val = getattr(self, name, None)
            # setattr(self, name, property(fget, fset))
            assign_as_property(self, name , fget, fset)

            self._condition_set(name, self, val)
            if val is None:
                continue

            if isinstance(val, Condition):
                self._condition_monitor(name, val)
                continue


        # self.__dict__.update(props)
    def _condition_monitor(self, name, cond):
        print('Should Monitor', self, cond)
        cond.bound_to = self
        cond._bound_name = name

    def _condition_get(self, name, parent):
        print(f'get "{name}" for {parent}')
        return parent.__dict__.get(name) or (getattr(self,name))

    def _condition_set(self, name, parent, value):
        print(f'set "{name}" for {parent}')
        # setattr(parent, name, value)
        parent.__dict__[name] = value
        self._condition.set(name, value)


class ConditionProxy(object):
    """Setting a key _here_ or on any bound Condition will propagate the
    change to all attached conditions. Each Condition will act according to
    its internal state.

        cp = ConditionProxy()
        cp.add(condition, condition2, condition3)

        # Through the proxy
        cp.bacon = True
        condition2.bacon == True

        # Through native propagate
        condition3.eggs = True
        condition.eggs == True
        condition2.eggs == True

    A condition may react to the set key to validate its internal state.
    """
    _conditions = None

    def get_conditions(self):
        return self._conditions or ()

    def add(self, *conditions, bind=True):
        """Store a condition into the internal maps
        """
        existing = self.get_conditions()
        if bind:
            for c in conditions:
                c.bound_to = self

        self._conditions = existing + conditions

    def __setattr__(self, k, v):
        if hasattr(self, k):
            return object.__setattr__(self, k, v)

        print(f'Settings "{k}" to conditions')
        for condition in self.get_conditions():
            # setattr(condition, k, v)
            condition.live_safe_set(k, v)

    def condition_emit_key_change(self, k, v, match, condition):
        print(f'Proxy heard change of, {k}, {v}', condition)
        for condition in self.get_conditions():
            condition.live_safe_set(k, v)

    def condition_emit_match_all(self, condition):
        print(f'condition_emit_match_all({condition})')

    def condition_emit_match_fail(self, condition):
        print(f'condition_emit_match_fail({condition})')


class MyLive(ConditionProps):
    """An example usage of the ConditionProps, integrating a live Condition with
    a working state entity.
    """

    # Required "target" state. Each key is tested upon set and
    # verified for an _eq_ state of the target value.
    condition_target = {
        "eric": True,
        "bob": True,
        "tom": True,
    }

    # Defaults if required
    eric = 4
    bob = True
    tom = None


    def condition_emit_match_all(self):
        """Called when the internal condition meets the target state.
        """
        print('MyLive condition match')


class Condition(object):

    target = None
    data = None
    bound_to = None
    # table = None
    met = False
    live = False
    store = False

    condition_emit_prefix = 'condition_'

    def __init__(self, target, data=None, table=None, bind=None):
        self.target = target
        self.data = data or {}
        self.bound_to = bind
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
        return self.live_safe_set(k, v)

    def live_safe_set(self, k, v):
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
        if match != currently_state:
            # A positive or neg change occured.
            self.emit_key_change(k, v, match)
        valid = self.self_assert()
        return valid

    def self_assert(self):
        met = self.test()
        if met != self.met:
            self.emit_wide_change(met == True)
        self.met = met
        return met

    def test(self, table=None):
        sv = set((table or self.table).values())
        # A set of one items with a value of 1
        return len(sv) == 1 and (tuple(sv)[0] == 1)

    def __eq__(self, other):
        if isinstance(other, bool):
            return self.met == other
        return object.__eq__(self, other)

    def emit_key_change(self, key, value, match):
        """A single key change
        """
        print(f'Key change "{key}" =={value}, valid:', match)
        n = f'{self.condition_emit_prefix}emit_key_change'
        if hasattr(self.bound_to, n):
            attrs = (key, value, match, )
            if self.bound_to != self:
                attrs += (self, )
            getattr(self.bound_to, n)(*attrs)

    def emit_wide_change(self, complete_match=False):
        print('Condition emit_wide_change')
        if complete_match:
            return self.emit_match_all()
        return self.emit_match_fail()

    def emit_match_all(self):
        print('Condition met', self.table)
        n = f'{self.condition_emit_prefix}emit_match_all'

        if hasattr(self.bound_to, n):
            attrs = ()
            if self.bound_to != self:
                attrs += (self, )

            try:
                getattr(self.bound_to, n)(*attrs)
            except TypeError as exc:
                print(f'Bound method error "{exc}" for condition: "{self}"\n'
                    'Ensure external condition hooks accept kwarg "condition"')

    def emit_match_fail(self):
        print('Condition fail', self.table)
        n = f'{self.condition_emit_prefix}emit_match_fail'

        if hasattr(self.bound_to, n):
            attrs = ()
            if self.bound_to != self:
                attrs += (self, )
            getattr(self.bound_to, n)(*attrs)


if __name__ == '__main__':
    c = main()
    print(f'Condition == "c" == {c}')
