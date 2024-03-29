# Connections 11.4.2

> Perform graph-like edge connections between anythings.

Building connections between _things_ in our code is fundamental to how out code operates. With graphs we build connection through _edges_, with each edge connecting to another node. It's a simple process but boring to program.

This library aims to simlify graph nodes and edge connections, decoupling the integration of graphs.

+ It's all about "edges"! no _nodes_ required
+ Anything is connectable (appliable to the graph), such as `ints` to `dicts`

```py
from g3 import Connections

import operator as op

d={}
c=Connections()
c.connect(0,1,2,3, data=op.mul)

c(0).data = 1.5
c(1).data = 2
c(2).data = 0.5
# don't change val c(3)

e = c(0).edges[0]
result = e.data(e.a.data, e.b.data)
assert result == 3

e = e.b.edges[0]
result = e.data(result, e.b.data)
assert result == 1.5


e = e.b.edges[0]
result = e.data(result, e.b.data)
assert result == 4.5
print(result)
```

## How it Works

The internal process is exceptionally simple - roughly 20 lines of code could replicate the core functionality. Upon `connect` each given unit (such as an `int` or `dict`) is stored in a flat dictionary. A unique ID assigns an "A" -> "B" connection to each unit - called an "edge".


