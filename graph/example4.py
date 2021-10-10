from pprint import pprint as pp

from graph import GraphTree, GraphNode
g = GraphTree()


g.connect('hallway', 'bedroom')
g.connect('hallway', 'small-room')
g.connect('hallway', 'bathroom')
g.connect('hallway', 'livingroom')
g.connect('hallway', 'kitchen')

g.connect('bedroom', 'bed', 'pillows')
g.connect('bed', 'blanket')
g.connect('bedroom', 'lamp')
g.connect('house', 'hallway')
g.connect('hallway', 'front-door')

n = GraphNode('fancynode', 'entity content')

g.connect('house', n)

f = g.find('hallway')

g.drain()
#f.view()
pp(f.chains())
