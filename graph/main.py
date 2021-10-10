"""
The Graph Tree unit stored GraphNodes in executable chains, living upon a persistent
event cycle. Although 'connected', graph nodes communicate through an _event chain_,
Of which sibling nodes apply an Event to a running (FPS) loop, passing and managing the
Event through the chain.

Each 'Entry' within the graph manifests as a int key, with an _pointer_ to the
real reference object. The real-reference may be a GraphNode, combining the
tree with an event executable chain.

Graphing process has a 3 distinct steps

Population Applied Nodes to the Tree in graph form - on a flat tree

Execution presents an 'event' to dispatch through the node tree, all target nodes
react the event, managing the dataflow.

Rendering builds paths and chains for linear execution of chosen flows.

---

Each node within the graph may have 1+ connected nodes, each node has further connections
or terminates with event actions. A 'node' is a graph point and may be _anything_. Utilising
the GraphNode tools, the graph entity may be 'callable' or a classy hook.

The Node amend and dispatches 'Events' propagated through the FPS loop, all event
tree exections are managed in the singular event engine. This allows nodes to signal,
with the ability to _stop_, inspect and kill a chain, governed by Node actions.

---

As the GraphNode content may be "anything", the asset collection through the
chain may be any developer useful content; such as a Graph of set(), or methods,
or _Reactive_ GraphNode Event executions.

---

When requesting a graph chain, the initial event marks the start node and
any arguments to provide across all nodes. For each node action subsequent steps
and calls will occur, the node (callable), returns any additional events to
continue the chain. They're pushed to the event stack of which is later drained.

    g.resolve('egg') -> button -> food

under-the-hood, the Egg node supplied a new "step" event to the 'button' node,
of which applies a "step" event to food.
Food will supply an _end of chain_ event, resolving one of many paths.

"""

from pprint import pprint as pp
from collections import defaultdict
import queue
import time

# from events import TreePump
from graph import GraphTree

FORWARD = 'forward'
REVERSE = 'reverse'
BOTH = ['forward', 'reverse']


def main():
    g = GraphTree()
    g.add({}, {1,2,3})
    # String assert as 1 id.
    g.add('egg', 'button')
    g.add('button', 'food')
    g.add('button', 'a')

    g.connect(*'LMONKEY')
    g.connect(*'LOTY')
    g.connect(*'LOBE')
    g.connect(*'HORSE')
    g.connect(*'HOUSE')
    # g.send('L', {}, on_end=fin)
    global d
    d=g.find('L', {}, on_end=fin)
    g.drain()

    test_find(d)
    return g

evs = { 'e': ()}

def fin(e,a,g):
    print('Finish', a, e)
    evs['e'] += (e,)
    # ev = e

def test_find(finder):
    ws = finder.events
    wq = evs['e']
    a = set(tuple(x.uuid for x in ws))
    b = set(tuple(x.uuid for x in wq))
    assert a == b
    print('Success')
    finder.view()


if __name__ == '__main__':
    g = main()
