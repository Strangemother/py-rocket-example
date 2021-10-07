from collections import defaultdict
from importlib import reload
from pprint import pprint as pp
from flatmap import FlatGraph

def main():
    g = FlatGraph()
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

    for item in g.walk('house'):
        print('item', tuple(item))
    #get('hallway', _g=g)
    pp(g.flat_chains(g.chains('lamp', with_parent=True, reverse=True)))
    return g


if __name__ == '__main__':
    g = main()

