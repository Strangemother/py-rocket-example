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

```py

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
```
