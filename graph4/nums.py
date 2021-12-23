"""This example presents the thin connections of a loaded unit - in this case 'ints'

As integer 0 to 3 with the edge data as a multiplier operator, for
each (manual) step through the connections, we yield a newly computed result.

This is easily resursive however the graph has a potential of exploding into
expontential paths.
This can be corrected by stashing a value into a dict, using the _current_
edge or node as the key (not displayed here).
"""
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
