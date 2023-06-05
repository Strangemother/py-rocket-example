# Issues

It's clear 'name by node' isn't helpful - as referencing the same function in the chain can be helpful. But this can quickly yield double-bound nodes:

    machine.connect(add2, add2)

    add2 -> add2 -> add2 -> ... -> add2
    add2 -> add2 -> ...
    add2 -> ...
    add2 -> <- add2
    add2 <-> add2

To fix this the user may apply a custom wrapper to _rename_ the secondary function

    machine.connect(add2, wrapper(add2))

However the wrapper may also be tagged as the unique node.

---

To solve this, potentially make the node name more unique. And functions are referenced in the node tree.

However this poses another problem when preferring to connect nodes directly.

    # with extra uniquenes..
    machine.connect(add2, add2)
    add2_a -> add2_b

Collecting the node later needs the real node:

    node_a, node_b = machine.connect(add2, add2)

