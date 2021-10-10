
```py
    3 4 5 6 7 8
---------------
3 | A
4 |         + + +
5 |         + + +
6 | + + + + + + +
7 |       +
8 |       +
---------------
>>> plot(1,8)
(None, None, None, None, None, None, None, None)

>>> step_resolve()

Reading 24 "none" spaces.
No movement.
Result 24 None spaces

    0 1 2 3 4 5 6 7 8
---------------------
0 |         + + +
1 |         + + +
2 |         + + +
3 | A
4 |         + + +
5 |         + + +
6 | + + + + + + +
7 |       +
8 |       +
---------------------
>>>
```

## Seeding

Sometimes the graph cannot plot, and _stepping_ into new cells yields an empty position. The `print_mem()` function presents the empty position as `+`.



```py
>>> step_resolve()
Reading 32 "none" spaces.
No movement.
Result 32 None spaces
---------------------
0 | J K J         + + +
1 | I A I         + + +
2 | B K J N       + + +
3 |   A I A P
4 | R S M   O + + +
5 | + + W   E + + +
6 | + + R S T + + +
7 |       + + + + +
8 |       + + + + +
---------------------
```

Another `plot` does not _flow_ as a rule cannot resolve on any _empty_ cell.

```py
>>> plot(7,6)
(None, None, None, None, None, None, None, None)

>>> print_mem()
---------------------
0 | J K J         + + +
1 | I A I         + + +
2 | B K J N       + + +
3 |   A I A P
4 | R S M   O + + +
5 | + + W   E + + +
6 | + + R S T + + +
7 |       + + + + +
8 |       + + + + +
---------------------
```

So we `force` a seed at our target position. This selects from all possible nodes
for the grapg

```py
>>> plot(7,6, force=True)
Nothing reduced, return all possible nodes
('M',)
>>> print_mem()
---------------------
0 | J K J         + + +
1 | I A I         + + +
2 | B K J N       + + +
3 |   A I A P
4 | R S M   O + + +
5 | + + W   E + + +
6 | + + R S T + + +
7 |       + + + M +
8 |       + + + + +
---------------------
```

When we step_resolve again, this new cell _should_ seed in 7+ directions.

```py
>>> step_resolve()
Reading 29 "none" spaces.
No movement.
Result 18 None spaces
-----------------------
0 | J K J         + + +
1 | I A I         + + +
2 | B K J N       + + +
3 |   A I A P
4 | R S M   O + + +
5 | + + W   E K L K J
6 | + + R S T A P A P
7 |       + B N M N M
8 |       + I A W A
9 |         R
-----------------------
>>>
```

With no movement, more steps will not resolve. Another 'seed' or more rules are required.


## Update Layers

Graph 'layers' are simply `A -> through -> B` rules, structured in a readable _mini_ grid:

    ASD   CXN   QSE
    GTF   PWF   ASD
    TRE   TRF   VFC

We apply each 'block' as single layers. Each char represents a _cell_ I'd plot in a wave.

Continuing from above, we can extend a partially built graph with additional layers, or simply AB rules:

```py
# One 'block'
g = stash(['ASD', 'GTF', 'TRE'])
# an AB Rule
stash(['KA'], *g)
```

In the first example we build a new graph from one block, a layer of 3 rows. The second example applies one rule "K" -> "A" and _updates_ the same graph.

Updating helps resolve a deadlock on-the-fly. Here we have the _locked_ part of a graph (from above).

```py
4 | R S M   O + + +
5 | + + W   E K L K J
6 | + + R S T A P A P
7 |       + B N M N M
8 |       + I A W A
9 |         R
```

We can _fill_ the waiting cells with one layer of possibilities.  Knowing relations `R`, `S` and `O` need additional rules, I apply a full-compass of rules:

```py
layer = [
    'RSM',
    'OPW',
    'EKR',]

stash(layer, *g)
```

When we attempt to resolve, the wave will collapse across all possible nodes:

```py
>>> step_resolve()
Reading 15 "none" spaces.
No movement.
Result 9 None spaces
-----------------------
0 | J K J         + + +
1 | I A I         + + +
2 | B K J N       + + +
3 |   A I A P
4 | R S M   O R S T
5 | A P W   E K L K J
6 | E K R S T A P A P
7 |       P B N M N M
8 |       P I A W A
9 |         R
-----------------------
>>>
```

As expected we _filled_ the empty cells. Notably the plotted elements are _relatively_ predictable but not exact. To continue, we could `plot` collapse to the empty spaces, or _seed_ within the empty cells.

```py
>>> plot(1,9, force=True)
Nothing reduced, return all possible nodes
('S',)
>>> print_mem()
-----------------------
0 | J K J         + + + +
1 | I A I         + + S +
2 | B K J N       + + + +
3 |   A I A P
4 | R S M   O R S T
5 | A P W   E K L K J
6 | E K R S T A P A P
7 |       P B N M N M
8 |       P I A W A
9 |         R
-----------------------
>>>
```


```py
>>> step_resolve()
Reading 10 "none" spaces.
No movement.
Result 0 None spaces
-----------------------
0 | J K J         P W A E
1 | I A I         M R S M
2 | B K J N       W O P W
3 |   A I A P
4 | R S M   O R S T
5 | A P W   E K L K J
6 | E K R S T A P A P
7 |       P B N M N M
8 |       P I A W A
9 |         R
-----------------------
>>>
```
