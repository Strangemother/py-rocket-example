# Functional Node connection

All nodes within the graph connect outside the functional nodes.
Connecting nodes through edges connects the functionality of each.

The 'edge' may perform transport cleanup, when bridging two nodes.
Functionality each node is a method or function, performing actions from the inbound graph calls. by default the call is stateless.
Outbound messages may channel through edges naturally or logically


Manual edge choice through logic. `REF` is placeholder for the future more elegant solution.

```py
def func_a(val:int):
    if val > 1:
        REF.upper_edge(val)
        return
    REF.lower_edge(val)
```

The call to `REF` is a lazy flag for after this function is complete.
A node is the same, without the functional wrapper.

```py
# node: func_a
if val > 1:
    REF.upper_edge()
    return
REF.lower_edge()
```

The graph stepper understands `func_a` called all references through _upper_ and _lower_ edge, passing `val`.

```py
g.connect(func_a, func_b, through=upper_edge)
g.connect(func_a, func_c, through=lower_edge)
g.connect(func_a, func_d, through=lower_edge)
```

