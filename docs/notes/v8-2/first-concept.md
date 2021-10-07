# Chains

The chains allow auto long wire connections

When connecting nodes

if a node is within a chain, a new chain is created.

    -A---B---C-     -A---B---C-
         |          -A---B---E---F-
    -D---E---F-     -D---E---F-
                    -D---E---B---C-

each item has a position in a table. Upon a instigator power event change
Each connected unit collects a background update

    A: 1
    B: 2
    ...
    F: 6


---

If one node in a chain is dead then all nodes are 0.

---

Each class node is bound to a list of ints for wire lines.
Upon calc, the class tests all lines for input.

A valid node:

1. may be `> 1` input
2. A multuplier of all nodes.


---

1. A class is a unit
    with a reference to a power table (and address)
2. Each call result stacks to a queue
3. digested by a compute loop.


This allows a 'message' - a function return, to be an addressed object. Either with a destination, or follow the given paths for the unit edges.


The 'loop' is an independant FPS clocked loop, accepting messages and pumping them to designated functions. Outputs may send the values to websockets - and thus other loops.


## IO

### Inputs

+ Websockets
+ Byte streams (from UI)
+ Terminal
+ HTTP Post (dev straight to the socket machine)

### Outputs


+ Websockets
+ Byte streams (from UI)


# Ownership

When a node enters the system its _owned_ by a "user" to assign input and output commands for the view vehicle. The 'originator' of the node owns the unit. If originator is not supplied, the unit is automatically assigned to the first owner within the attached parent list (upward), starting with the most immediate node, and ending with the _first_ node for all children - likely a 'ship'.

The physical nodes attach to output streams naturally, as all python units maintain an allowed connection to the output stream through the originator parent connection, messages to other nodes apply to the 'event stack', with the _next loop_ processing the event.


# Messages

All 'connected' nodes bridge through assigned edges for the loop reference. Fundamentally a node (being a software representation of a visual 'hardware' device) receives data through the pipe and pushes simple formatted messages back out - the event loop will manage the ferrying across the graph and to the view.

The message may have an address, such as another node. Without this address the message should follow the _standard path_ given through the graph edges.


---

1. A Node is 4th wall software for visual hardware devices
2. A node connects within a graph
3. of many nodes
4. It receives standard functional messages
5. and returns formatted messages
6. with an address pushes the message to a target
7. Else the message is process through the attached edges.

The loop of message transations lives independently of the nodes (albeit within the same thread) processing messages and mounting nodes.

+ A node has a table reference
+ With a power value and/or percentil
+ Processed by the loop
+ Pushing power calculations per message (if a change occurs)

# Power

The power of a unit is a terse calculation of electric, given a flat compute table and the edge list. Each node power calculates as the chain computes. For now a linear chain of multipliers.


