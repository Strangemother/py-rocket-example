# Edges

When creating an edge, the method of integration dictates how the edge computes the node.

If a custom edge is not applied, the default `LiveEdge` wraps a connection of two nodes. When inspecting the graph, collecting a list of edge returns a mixture of `LiveEdges` and any custom edge data.

As the _edge_ mostly acts as a pointer to the graph content, it's cheap to create. For the default `LiveEdge` we define it as a `factory` edge. Every time it's used, a new instance is generated and returned. If `factory=False`, the same instance is used for every call.

---

As an example, we can create a "Flip Flop" gate between two nodes. When testing the connection between two nodes (A and B), every _execution_ of our edge yields `0` or `1`, relative to its last call.

For each call the value is negated, `0` -> `1` -> `0` etc... When resolving our chain `A` => `B`, the result should yield:

    A, 0, B
    A, 1, B
    A, 0, B
    ...

When loading our edge, is should manage this though its factory. If a _complex edge_ is not given, such as a function or a dictionary, this does not occur:

```py

class Edge():
    factory = False
    val = 0

g.connect('A', 'B', edge=Edge())
g('B').edges
(<Edge>,)
```

In this setup, every call to an edge will affect this one value.


```py
class Edge():
    factory = True
    val = 0

g.connect('A', 'B', edge=Edge())
g.connect('A', 'B', edge=Edge)

g('B').edges
(<Edge>,)
```

The two example are essentially the same, If the unit is a factory, but is an object instance, a new instance of the class is discovered.

In both cases a new edge is created upon repeat calls, yielding initial values for the value:

    A, 0, B
    A, 0, B
    A, 0, B

