# Graph Collapse

A simple wave-function-collapse-like resolver.

To display its functionality we start with the most simple example:

```py
la = [
    'AAA',
    'AAA',
    'AAA',
]

g=stash(la)
```

The stepping tool is prepared, we can plot a pseudo grid of locations using this "memory":

```py
mem = {
    (3,3): 'A',
}
```

We ask for some resolved cells:

```py
collapse(6,3)
collapse(6,4)
collapse(6,5)
collapse(6,6)
collapse(7,6)
collapse(8,6)
```

and present the current state:

```py
>>> print_mem()
---------------
3 | A
4 |
5 |
6 | + + + +
7 |       +
8 |       +
---------------
```

The plus `+` sign presents uncollapsed cells or locations within the graph of which did not yield a successful node type, because there was no _seed_.

We can ask to _recursively resolve until all possibilities are done_ with `step_resolve()`.

```py
>>> step_resolve()
Reading 6 "none" spaces.
No movement.
Result 6 None spaces
---------------
3 | A
4 |
5 |
6 | + + + +
7 |       +
8 |       +
---------------
```

As we can see no changes because the graph cannot seed this location. We can `plot()` our movement, asking the graph to start _collapsing_ near the given position

```py
>>> plot(1,3)
(None, None, None, None, None, 'A', 'A', 'A')
>>> print_mem()
    2 3 4
---------------------
0 | + + +
1 | + + +
2 | A A A
3 |   A
4 |
5 |
6 |   + + + +
7 |         +
8 |         +
---------------------
```

we can see it _nearly_ resolved, but the neighbour did collapse, because of the
proximity to an existing node.

We can as to _resolve as must as possible_ with `step_resolve()`

```py
>>> step_resolve()
Reading 11 "none" spaces.
No movement.
Result 6 None spaces
---------------------
0 | A A A
1 | A A A
2 | A A A
3 |   A
4 |
5 |
6 |   + + + +
7 |         +
8 |         +
---------------------
```

If we seed another location and perform another collapse, all empty cells connected
to a collapsing cell will also collapse:

```py
>>> plot(6,1, force=True)
Nothing reduced, return all possible nodes
('A',)
>>> print_mem()
---------------------
0 |   A A A
1 |   A A A
2 |   A A A
3 |     A
4 |
5 |
6 | A   + + + +
7 |           +
8 |           +
---------------------
```

`step_resolve` iterates the _resolve_ function until the number of changes per iteration hits 0. In this case all empty nodes.

```py
>>> step_resolve()
Reading 5 "none" spaces.
No movement.
Result 0 None spaces
---------------------
0 |   A A A
1 |   A A A
2 |   A A A
3 |     A
4 |
5 |   A A A
6 | A A A A A A
7 |   A A A   A
8 |           A
---------------------
>>>
```

## Wider Collapse

Perhaps you have a grid (memory) of many waiting spaces and want to seed and collapse:


```py
>>> plot(5,9, force=True)
Nothing reduced, return all possible nodes
('A',)
>>> print_mem()
-----------------------------
-1 |           + + + + +
0 |       + + + + + + +
1 | + + + + + + + + + +
2 | + + + + + + + + + +
3 | + + + + + + + + + +
4 | + + + + + + + + + + + +
5 | + + + + + + + + + + A +
6 |     + + + + + + + + + +
7 |       + + + + + + +
8 |           + + + + +
9 |           + + + + +
10 |           + + + + +
-----------------------------
```

The step resolve will continue through all uncollapsed nodes until no movement.

```py
>>> step_resolve()
Reading 90 "none" spaces.
No movement.
Result 0 None spaces
-----------------------------
-1 |           A A A A A
0 |       A A A A A A A
1 | A A A A A A A A A A
2 | A A A A A A A A A A
3 | A A A A A A A A A A
4 | A A A A A A A A A A A A
5 | A A A A A A A A A A A A
6 |     A A A A A A A A A A
7 |       A A A A A A A
8 |           A A A A A
9 |           A A A A A
10 |           A A A A A
-----------------------------
```

In this case, because the rule is so robust ('A' will always yield 'A'), the
entire graph populates without locking.


### Extend

```py
la = [
    'AAA',
    'ABA',
    'AAA',
]

g=stash(la, *g)

>>> print_mem()
-----------------------------
-1 | + + +       + + + + +
0 | + + + +     + + + + +
1 | + + + +     + + + + +
2 |   + + +     + + + + +
3 |       +     + + +
4 |         + + + + + +
5 |         + B + + + +
6 |       + + + + + + +
7 | + + +       + + + +
8 | + + + +     + + + +
9 | + + + +       + + +
10 |   + + +   +
-----------------------------
>>> step_resolve()
Reading 60 "none" spaces.
No movement.
Result 0 None spaces
--------------------------------
-1 | A A A       B B A B A
0 | B A A B     A A A B B
1 | B B A A     A B B B A
2 |   A B A     A B A A B
3 |       B     A A B
4 |         A B B A A A
5 |       B A B B A A B
6 |     A A B A A B B B
7 | A A B B A   B B B A
8 | B A A B     A A A B
9 | A B A B B A B A A A
10 |   A B A A + A
11 |         B A A
--------------------------------

```

## Slurp Plot

```py
---------------
3 | A
4 |
5 |
6 | + + + +
7 |       +
8 |       +
---------------
>>> slurp_plot
<function slurp_plot at 0x0000000002B1E7B8>
>>> slurp_plot(6,3)
((5, 2), (5, 3), (5, 4), (6, 2), (6, 4), (7, 2), (7, 3), (7, 4))
>>> print_mem()
---------------
3 |     A
4 | + A A
5 | A + A A
6 | A A A A + +
7 |   A A A   +
8 |           +
---------------
>>> step_resolve()
Reading 4 "none" spaces.
No movement.
Result 0 None spaces
---------------
3 |     A
4 | A A A
5 | A A A A
6 | A A A A A A
7 |   A A A   A
8 |           A
---------------
>>> flush()
---------------
3 |     +
4 | + + +
5 | + + + +
6 | + + + + + +
7 |   + + +   +
8 |           +
---------------
```

Further resolve (empty spaces in this case) at a target location:

```py
>>> step_resolve(3,4)
Reading 8 "none" spaces.
No movement.
Result 25 None spaces
-------------------
1 |   + + + + +
2 |   + + + + +
3 |   + + + + +
4 | + + + + + +
5 | + + + + + +
6 | + + + + + +
7 |   + + +   +
8 |           +
-------------------
```

```py
>>> plot(7,3, force=True)
Nothing reduced, return all possible nodes
('A',)
>>> print_mem()
-----------------------
0 | + + + + +
1 | + + + + + +
2 | + + + + + +
3 | + + + + + +
4 | + + + + + +
5 | + + + + + +
6 | + + + + + +
7 | + + A + + +
8 | + + + + + +
9 | + + + + + +
-----------------------

>>> step_resolve()
Reading 57 "none" spaces.
No movement.
Result 0 None spaces
-----------------------
0 | A A A A A
1 | A A A A A A
2 | A A A A A A
3 | A A A A A A
4 | A A A A A A
5 | A A A A A A
6 | A A A A A A
7 | A A A A A A
8 | A A A A A A
9 | A A A A A A
-----------------------
>>>
```

```py
la = [
    'AAA',
    'ACA',
    'AAA',
]

g=stash(la, *g)
flush()
>>> step_resolve()
Reading 48 "none" spaces.
No movement.
Result 0 None spaces
-----------------------
0 | A A A B A
1 | B B B A A A
2 | B B A B A A
3 | A A B B B B
4 | A A B A B B
5 | A B B A B A
6 | A A A B A A
7 | A B B A A A
8 | A B A B B B
9 | A B A A A A
-----------------------
>>>
```
