Graph 2 worked very well however when submitting a connection between many complex edges (and overridding nodes), the complexity to pass values is difficult.

A complete reset of the internal functionality should fix this problem:

## It's all about edges.

The dictionary data for a 'node' is a stardard dict. Applying a transient stepper in the form of an event loop allows automatic outbound communciation of the node. Alternatively stepping the tree and processing edge connections is also possible.

The node tree is built of 'edges' only. Each Edge connects a dict key to dict key. The user "node" may be anything (not just a Graph type) as iterating a list of independent edges may persist computes.

1. Build a connection list of edges, positionally connected to a real _node_.
2. Call upon edge connections, yielding 'keys' to resolve into the _node_ or user entity attribute
3. Data changes occur outside the changing states, as we're dealing with a list of edges only.

===

The `Edge` stored A to B, or potentially A to many B. This is uni-directional, however simply _switching_ the keys may bind a reversal.

+ Many edges for one key.
+ An edge stores 2+ keys and its value (labels, weights)
+ The edge can have "Transport" and "tap" methods.
+ A "node" in edge reference is just a name.
+ A "Node" wraps the string into a useful unit (walkers etc.)

---

If an "edge" contains a "get value", the target entity may exist as a global or a dict within a dict.

```py
units = {
    'a': {}
    'b': 1
}

other = {
    'c': []
}

edge = connect('a', 'b', refs=(units,units,))
edge = connect('a', 'c', refs=(units, other))
edge.get_next()
# Node('b', 1), Node('c', [])

edge = connect('a', 'b')
edge.get_next() # 'b'
```

---

The EdgeTree, keeps a list of all A to B connections, and their custom edge type.
A user can spawn a 'node' from the tree, of which is a thin wrapper for an edges A ref.

The node allows a user to step through the edge, gathering values and new nodes.
The "node" itself is very cheap. A user can utilise anything as a node, given the edge references are significantly unique.

The edge can store a "key" of anything, converting the _input var_ key as an ID'd unit, storing the "hash id" to an edge reference.

The user node has a reference in the tree and its sibling edges.

    tree = {
        nodes: DTree {
            a_id: a
            b_id: b
            c_id: c
        }

        up: SetTree { ... }
        reverse: SetTree { ... }
        forward: SetTree {
            a_id: <set> { eid_1, eid_2 }
            b_id: {}
            c_id: { eid_3 }
            d_id: {}
        }

        edge_connections: DTree {
            eid_1: a_id, b_id
            eid_2: a_id, c_id
            eid_3: c_id, d_id
        }

        edge_data: DTree {
            eid_1: { transports, weight, label, taps }
        }
    }



---

The DTree is a simple defaultdict, with the ID being a reference to the stored item.
If a UUID is given upon input, the unit should accept the ID with a `receive_id(uuid)` function.

A SetTree provides a simple Set list for an ID. `tree.get('a') == {eid_1, eid_2}`.


For both types, given a `resolve` target, the get result may collapse into the real unit (not just the ID.) `tree.get('a') == { Edge, Edge}`

Notably an "Edge" is any class, with the ability to accept and yield the _next_ IDS.


## Default Edge

If a unique edge is not required (a default "global" edge, or _no edge_), the direction tree may yield a generic class, instaniated upon runtime. The edge ID given in the SetTree may be the forward entity ID. Importantly this is fine for internal detection, but exporting the data should collapse this correctly, else other units may not follow the same course.

Furthermore, a default edge should not maintain all outbound nodes to all other edges, as that's easy to leak. Storing a new edge instance for every default edge is wasteful. This should be easy to fix with a "get edge or fallback to node" - or a SetTree fallback:

    tree = {
        nodes: DTree {
            a_id: a
            b_id: b
            c_id: c
        }

        forward: SetTree {
            a_id: { eid_1, c_id }
            b_id: {}
            c_id: { eid_3 }
            d_id: {}
        }

        edges_connections: DTree {
            eid_1: <Edge> a_id, b_id
            eid_2: a_id, c_id
            eid_3: c_id, d_id
        }
    }

```py
tree.forward['a_id'] == <edge a_id b_id> <default edge a_id c_id>
```


## DictEdges (EdgeMount)

Using an autodict can transmit content the edges, emission occurs across all edges automatically.

when changing a value in the dict, announce the change in the edge tree.

    d = {
        foo: 1
    }

    edges.prop('foo', 1)

All edges should respond accordingly.

---

directions act as a compass, mapping directions through automation:

    forward: reverse
    up: down

     -3       -3       -3
         5     6     7
            2  3  4
     -5  4 -1  0  1  0  1
           -4 -3 -2
         3     2     1
     -7       -5       -3


     -4       -4       -4
         6     7     8
            2  3  4
     -6  5 -1  0  1  1  2
           -4 -3 -2
         4     3     2
     -8       -6       -4


      7        9        11
         5     6     7
            2  3  4
      3  4 -1  0  1  0  1
           -4 -3 -2
         3     2     1
     -1       -1       -1



      8       10       11
         6     7     8
            2  3  4
      4  5 -1  0  1  1  2
           -4 -3 -2
         4     3     2
      0        0        0


Selecting from the _compass_ direction is easier to read:

here = 0
up = n = 3
down = s = -3
forward = e = 1
backward = reverse = w = -1

nw = n + w
ne = n + e
sw = s + w
se = s + e

reverse == -forward
s = -n
up + down == here
here == n + s + w + e

