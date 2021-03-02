# SuperGrid

The Grid identifies a wave function collapse _like_ step testing for node assignment,
with additional _collapsable_ grids above and below a grid node. This supplies a 3D cube grid to collapse in 6DOF. Fundamentally we cater for one node. The node has possible siblings chosen by _collapsing_ the neighbours, or through manual choice.


For each node, find possible node given its neighbours including above and below.
A neighbour may be "blank" or null - or only have _one direction_ with collapsable possibilities.


# Node Collapse

When collapsing a node, it should be the lowest entropy choice of all neighbour node allowances.
We start at a node `(5,4)` (BOB) with its _right side_ neighbour `(5,5)` of a defined value - thus has one state.

First we identify all possible states for the node; `0` though `9`, then reduce the possibilities given existing neighbours.

Gather Bob existing neighbours: N|S|E|W|A|B. For each node define the allowed sibling of the target node face, e.g The `S` face for `N` of Bob, the `W` for the `E` neighbour and so on.

Given a list of _allowed_ node for each collapsed neighbour, delete any unwanted from the target node possibilities. This results in a reduced list of allowed choices for the current node "Bob".

The same can be done for _unplotted_ neighbour nodes, allowing an uncollapsed point to provide gravitas on the incoming node choices. In theory this is only relevant if the empty space reserves position knowledge, such as a grid limit or a relation to another collapsed node.

Choose a type from the final list and plot.

---

When an empty node is collapsing possible choices, it may not be the _target_ node and therefore will not finalise a collapse. This is the case for _neighbour_ tests and cursory distance tests.


The datanodes act like a sparse matrix to identify already solved positions within the grid.

# Layer stepping

Each Layer consists of a 2D grid, complete with 1+2N nodes. Step direction and indexing supply the compass direction for later traversal.

When iterating _rows_ of a layer, stepping left to right yields _to EAST_ `(0, 1)`. Zero being the _current node_ within a row. Stepping occurs through relative indexing:

    -1  1  1      M N O
    -1  0  1      W A E
    -1 -1  1      R S T


        UD   LR     D
place    0    0     A
east     0    1     E
west     0   -1     W
south    1    0     N
north   -1    0     S
NE       1    1     O
SW       1   -1     M
NW      -1   -1     T
NE      -1    1     R


## Uncollapsable positions

In some cases a cell may collapse but may not contain enough sibling information to determine a node choice, a `None` entity returns for the space. This occurs when an _allowed_ node type is not supplied, but the collapse may occur with _any_ node. This can be enforced during the collapse stage.


```py
{'A'}
{(2, 3): 'A',
 (2, 4): 'A',
 (2, 5): 'A',
 (2, 6): 'A',
 (3, 3): 'A',
 (3, 6): 'A',
 (4, 6): 'A',
 (5, 3): 'A',
 (5, 4): 'A',
 (5, 5): 'A',
 (5, 6): 'A',
 (6, 3): None,
 (6, 4): None,
 (6, 5): 'A',
 (6, 6): 'A',
 (7, 5): 'A',
 (7, 6): 'A',
 (8, 6): None}
    2 3 4 5 6 7 8
-----------------
2 | A A A A
3 | A     A
4 |       A
5 | A A A A
6 | + + A A
7 |     A A
8 |       +
-----------------
>>> plot(5, 3)
```

In this example we have a single layer of `A` chars. The `+` identifies `None` placements, where the _collapse_ did not succeed, thus producing a null entity. This can be fixed with `force`

    plot(5,3, force=True)

Ensuring the collapse will pick a node from all possible nodes. Alternatively collapsing a neighbour may yield options.



## Layer Populating

    layer = [
        'MNO',
        'WAE',
        'RST',
    ]

    la = [
        'AAA',
        'AAA',
        'AAA',
    ]
        g1=stash([
            'JKL',
            'IAP',
            'BNM',
        ], *g)

    print_mem()

       3 4 5 6 7 8 9 10
    --------------------
    3 |     A
    4 |   A E   L + J K
    5 | A E A A P + I
    6 | A R N T T + B N M N
    7 | A A P E + + W
    8 |     S T + + R S T
    9 |       + + + + +
    10 |       + + + + +
    --------------------

    stash(['LAJ'], *g)
    print_mem()

    --------------------
    3 |     A
    4 |   A E   L A J K
    5 | A E A A P S I
    6 | A R N T T + B N M N
    7 | A A P E + + W
    8 |     S T + + R S T
    9 |       + + + + +
    10 |       + + + + +
    --------------------

    stash(['TTIB', 'EAST'], *g)
    step_resolve()

    -----------------------
    3 |     A
    4 |   A E   L A J K
    5 | A E A A P S I
    6 | A R N T T T B N M N
    7 | A A P E A P W
    8 |     S T T I R S T
    9 |     E R S T I O
    10 |     T N E A A A
    11 |     A A A
    -----------------------

plot(6,8)
plot(6,10)
step_resolve()
plot(6,10, force=True)
step_resolve()
print_mem()
step_resolve()

## Movement

```py
>>> step_resolve()
Reading 25 "none" spaces.
No movement.
Result 25 None spaces
    3 4 5 6 7 8 9 10
--------------------
3 |     A
4 | A A E       O + + + +
5 | A S M N     E + + + +
6 | N O W A R S T + + + +
7 |   E R N O + + +
8 |         E + + +
9 |       S T + + +
10 |         + + + +
--------------------
>>> step_resolve()
Reading 25 "none" spaces.
No movement.
Result 25 None spaces
    3 4 5 6 7 8 9 10
--------------------
3 |     A
4 | A A E       O + + + +
5 | A S M N     E + + + +
6 | N O W A R S T + + + +
7 |   E R N O + + +
8 |         E + + +
9 |       S T + + +
10 |         + + + +
--------------------
```

The graph is _stuck_ and manual intervention can fix the stitch:

```py
>>> stash(['EA'], *g)
```

Applying a new connection `E` -> east -> `A` provides 1 extra rule, allowing
position `(5,10)` to collapse and cause a persistent wave through all _waiting_
cells:

```py
>>> step_resolve()
Reading 19 "none" spaces.
No movement.
Result 1 None spaces
    3 4 5 6 7 8 9 10 11
-----------------------
3 |     A
4 | A A E       O K L K O
5 | A S M N     E A E A A
6 | N O W A R S T S M B S
7 |   E R N O M O L W
8 |         E A A P
9 |       S T S N A
10 |         + W A N
11 |           R
-----------------------

>>> step_resolve()
Reading 3 "none" spaces.
No movement.
Result 10 None spaces
    3 4 5 6 7 8 9 10 11 12 13
-----------------------------
3 |     A
4 | A A E       O K L K O
5 | A S M N     E A E A A
6 | N O W A R S T S M B S
7 |   E R N O M O L W
8 |         E A A P
9 |   + R S T S N A
10 |   + + + + W A N
11 |   + + + + R A
12 |   + + + + + S
13 |   + + + + + +
-----------------------------

>>> step_resolve()
Reading 17 "none" spaces.
No movement.
Result 0 None spaces
    3 4 5 6 7 8 9 10 11 12 13
-----------------------------
3 |     A
4 | A A E       O K L K O
5 | A S M N     E A E A A
6 | N O W A R S T S M B S
7 |   E R N O M O L W
8 |         E A A P
9 |   M R S T S N A
10 |   A A K O W A N
11 | R R S A J R A
12 |   W B E A A S
13 |   R S A N S M
-----------------------------
>>> step_resolve()
```
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
