# Paths

A path defines a walking route through the graph. By default they are generated when one or more nodes are bound through `connect()`.

```py
g = graph.Graph(id_method=None)
path = g.connect(*'BANANA')
(4, 1, 1, 0, 1, 0)
```

Paths provide deterministic routes through the graph, based upon given connection.
Upon creating a chain of linear connections, the "edge positions" provide a stepping route from _start_ to _end_ without knowledge of the node.

In the "Pinafore" example, all the sentences generate _position paths_ for each line. When graph binds the given _word_ nodes, route entropy may produce unwanted paths:


    I've information vegetable ...
    ... In short, when I've a smattering of ...
    ... fugue of which I've heard the music's ...


Connecting the term `I've` and `a`|`heard`|`information`, yielding a bad route. The _position paths_ write three distinct routes.


## Path Graph (4D Inverse)

Beneath the graph of elements, all the nodes connect through edges. A _position graph_ allows inspection of the built connections through `Graph.paths`.

For each node a connection (through an edge) builds its own graph. Each node connection maintains a _vector_, `x` as the row, and `y` as the node edge list column index. A node may connect to many other nodes, so the `Graph` builds an internal graph of these "edge index to edge index" connections.

This is hard to visualise so here's an image:

![inverse graph](./images/inverse graph.PNG)

And the sibling code:

```python
import graph
from graph import Edge, BlankEdge

g = graph.Graph(id_method=id_method)
g.connect(fa, fb, fc, fd, edge=Edge())
g.connect(fa, fab, fac, fad)
g.connect(b_a, b_b, b_c, b_d, edge=BlankEdge())

g.add_edge(fc, fd, edge=Edge())

g.connect(fb, fd)
g.connect(fa, fd)
g.connect(fc, fab)
g.connect(fab, b_a)
g.connect(b_c, fad)

positions_graph = g.paths # <Graph>
```

In the example we can see two visualisations for the same (functions) graph. The larger graph presents the linear connections I've applied during creation. The second graph presents the internal positions graph of the parent nodes built automatically.

The positions graph may be considered the "4D inverse" of the parent graph, where the parent graph inverts _through itself_ and presents all its bones. Another analogy may be 'folding a ball inside-out', where the wall of the this imaginary sphere can pass through its itself. However instead of a sphere, we have a "blobby shape" and no walls.


### Deeper (5D and Beyond)

Beneath `Graph.paths`, a `paths` manages the list of connections with the parent graph. As `Graph.paths` is the _inverse_ of our parent, the `Graph.paths.paths...` are additional inverse dimentions of the parent graphs. Through reducing entropy, after a certain depth the graph will repeat itself. By default the graph will stop recursing after a depth of `>5`. Notably The 5D graph (Inverse of the inverse) is not a mirror of original 3D `(n-2)e01` graph, as we're reducing _down_ through dimensions.



# Reading Paths

Each graph connection builds a bridged path, for chained execution across the graph through the given nodes. Notice the path index is deterministic for early and late positions, (ABCD and APPLES), and intial-referencing, for example "P" to "P" is of index 0, noting the first graphed for the Node "P" was "P".

```python
g = graph.Graph(id_method=None)#id)
g.connect(*'ABCD')
g.connect(*'DEFGHIJKL')
g.connect(*'DOGGY')
g.connect(*'HORSE')
g.connect(*'MOUSE')
g.connect(*'BANANA')
g.connect(*'APPLES')
```

Producing a int position paths:

    ABCD      (0, 0, 0, 0)
    DEFGHIJKL (1, 0, 0, 0, 0, 0, 0, 0, 0)
    DOGGY     (1, 1, 0, 1, 2)
    HORSE     (2, 1, 1, 0, 0)
    MOUSE     (3, 0, 2, 0, 0)
    BANANA    (4, 1, 1, 0, 1, 0)
    APPLES    (0, 2, 0, 1, 0, 1)

To read a path, iterate each index relative to the graph position of the previous node:

    BANANA    (4, 1, 1, 0, 1, 0)

The first value is the start _pin_. The integer (position `0`) denotes the output edge from the _start pin_. In the above example the `A` node appears twice with position `0`. The letter `D`, has the _start pin_ next output edge `1`. For our word "Banana", we see the `B` was inserted at position `4`:

```python
tuple(g.start_pins)[4]
"B"
```

from `B` we can walk forward with the path `[..., 1, 1, 0, 1, 0]`. Each node resolves to an ordered list of _next_ keys (no edges involved)

```python
>>> tuple(g.tree.forward['B'])
('C', 'A')
```

We can see the next possible steps from `B` are `C` and `A`. Notably our "banana" next target letter `A` is the index `1`. We can build the full word with the correct path, knowing are start letter `B`:

```python
v=('B',)
p = (1,1,0,1,0)

for i in p:
   n = tuple(g.tree.forward[v[-1]])[i]
   v += (n,)

print(v)
('B', 'A', 'N', 'A', 'N', 'A')
```

