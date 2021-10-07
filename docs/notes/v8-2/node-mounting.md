# Node Mounting

A node consists of a single machine unit, connected to other nodes through the graph, communicating changes through the socket pipes.

A Node

+ doesn't generally have reference to the UI
+ maintains a unique ID; same for the unit and socket
+ has a persistent anonymous socket connection
+ connected through a graph
+ communicates changes through object events


## What is a Node

A single "node" references a software representation of a visual _hardware_ device, such as a shoe, switch, LED, or space-ship. All nodes connect through edges to other nodes, allowing pathed signals for events.

The node wholeheartedly exists alone, being self sufficient with the correct inputs. Consider an LED will _be lit_, if a power connection exists. The changes or actions taken emit as object from the functional calls, formatted to the correct stream output through a designated socket


## Output Sockets

The node should communicate to the best available client. Notably this should be the original owner of the node (the code). As a new node is created, the assigned 'owner' may exist, to ensure the web socket throughput ferries information to the correct UI instances.

If a newly created node has no owner (thus the node is currently an orphan), the parent graph populates the value with the first discovered, whilst working up the chain to designate 'paths'.

The output socket is web-socket or terminal pipe, emitting and receiving a byte stream or string formatted object. A node should simply "send a message", and it's routed to the correct parents, and the correct output streams.


### Web Socket Automation


Every class instance "node" is automatically connected to an open websocket, to emit debug info, to a waiting graph view. The initiating source maintains a persistent 'backbone', to the ready websocket, and thus its connected interfaces.

The node doesn't allocate or address the socket as the `send` command expects a protocol formatted message. Every _waking_ node emits a "new" message and any new instance meta (e.g. display color and label), for waiting interface clients.

The client interface is also connected to the websocket backbone - as a single "visual" client, in this case a debug view with the ability to decode the wake message.


## Parenting

Each node should connect to a _previously_ created node, within the edge graph. If a newly created node is not connected, it's considered an "orphan" and will not receive natural events, or emit through the graph.

The uppermost node (the very first or a designated 1st order node) is a 'parent' is no nodes _above_. In game lore this is a "ship" and all its attached software, or a battery as part of a circuit. All of which _Start_ with the owner of the edges path.


## Auto Graph

All nodes should be connected to other nodes in either a forward or reverse direction along edges in a graph, relative to the start node and the initial node, the first "parent" node.

The edges tool and implementation has no effect on the node unit, as such is essentially an anonymous wire edge set, allowing piped messages without specific node logic. The graphing strategy lives independently of the nodes - much like a device _wired_ to another; the wire doesn't define the state of the device.


---

# Startup

A node "Wakes up" through instantiation, emitting a silently failing message to the pipe. The startup script should bind new edges, and infer the bridged paths when connected.

A node is connected to a few smaller graphs.

1. The 'ship' unit - a logical connection through rooms; or a patch panel.
2. Wires for data and power
3. sub software graphs

The Data connections are easy, by simply defining edges for sporadic immediate messages. This works well for the ship flight matrix (AFS) and game hardware level connection (e.g. simulated USB)

Power required further study and may be found in the readme of this content.

1. Power chains has its own message rules
2. with a flat compute table for power values
3. an address for every node, each node storing power consumption
4. At a tick of 1FPS, and a subtick of 10FPS (coulombs calculation)
5. and event funtion callback (`power_off()`, `explode()` events)

The 'power' chain, and 'data' chain live through the ship to manipulate. The 'parent' graph exists for logical relationships and is more focused on "things touching", such as a graph of floor panels.

