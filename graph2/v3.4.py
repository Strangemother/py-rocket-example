"""

An 'operator graph' should bind to a dictionary of values. Each step in the operator
manipulates the data. Operators act automatically, calling forward upon a change.

"""

from graph import Graph, Edge, Node, NodeList
import operator
import errors

g = Graph()
g.connect(*'abcd')
g.connect(*'cfgh')
g.connect(*'gi')
g.connect(*'fi')

#set values
for x in g: g[x]=0
