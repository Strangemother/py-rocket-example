# Column Graph Walking

It's possible to walk the graph from _start_ to _end_ (or forever), in a column scanning method, similar to a barcode. Given a starting point, each step to connected nodes may yield further nodes. Consequently this can proceed forever.

With a "Bar Walker" you step the graph, reading the _current_ nodes for each iteration. The iterator (your loop) may act upon the graph values accordingly.

```bash
g = Graph()

# Submit unbound nodes, to unpack into a node and the data value.
a2 = Add(value=2)
mp5 = Mul(value=.5)
a1 = Add(value=1)

g.connect(a2, mp5, a1)

w = walker.bar_walk(g.get_start_node())
next(w)
(<Node "add_2">,)
next(w)
(<Node "mul_0.5">,)
next(w)
(<Node "add_1">,)
next(w)
```

This is fun but purposefully not smart. Recursion will occur if a node is connected to a ring (or itself). The `bar_walk` is synonymous with:

```py
last_result = nodelist # graph.get_start_node()
while step:
    v = last_result.values() # current list of stuff.
    step = bool(len(v))
    yield tuple(v) #

    new_res = {}
    for name, node in last_result.items():
        if is_exit(node): continue # <ExitNode>
        _next = node.get_next_flat() # Node or NodeList, list of all next nodes.

        for next_node in _next:
            if is_exit(next_node): continue # Ignore exists.
            new_res[next_node.name] = next_node
    last_result = new_res # all ready for the next step.
```

we assume `nodelist` is out entry point, to be replaced with the loop.
Given the _last value_ (or the first step), read each _next nodes_ for each stored item.
Produce a new dictionary of the _next nodes_ and overwrite the _last result_.

The `last_result` is a dict with `values()` similar to a nodelist - as such, each iteration returns a tuple of nodes the _last iteration_ recorded.

---

The _accept_ the result code should manipulate the graph dict data, or do whatever interaction really. At this point you may build your own event machinery using a such as the standard `asyncio`.

This joke should be extremely funny now:

> A Graph walks into a bar and the bar says: "Give me a drink, give me more drinks, give me no drinks, give many drinks..." forever.
