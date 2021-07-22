A simplified graph, to connect referenced items through a keystate connection.
Each connected node may have optional weighted Taps, allowing the alteration
of data through the pipe.

Graphing items should be maintained within the graph tree itself, the end user maintains the entities


```py
g = Graph()
g.connect(*range(9))
print(tuple(iter(g[3]))
(3, 4, 5, 6, 7, 8)

```

```py
import string
g = Graph()
g.connect(*string.ascii_lowercase)
```

+ A path has an automatic _start_ and an _end_ node
+ The `graph.connect` function appends many items in-order (a chain of nodes with no edges)



Storing values acts like a set(), where one of each unique entity is applied to the graph. When adding nodes, they apply new slots or silently update existing nodes.

```py
graph.connect(*'ABCD')
graph.connect(*'ABCDEF')
tuple(iter(g['A']))
['A', 'B', 'C', 'D', 'E', 'F']
```

Each node is connected to its sibling though `connect(a, b)`.
When using `add()` the nodes automatically bind to the _start_ and _end_ nodes of the graph. `connect()` does not automatically append the end nodes.




```py
g.add(*'AB')
g.connect(*'BC')
g.add(*'CD')
g[g.start_node].forward_nodes()
['A', 'C']
```
