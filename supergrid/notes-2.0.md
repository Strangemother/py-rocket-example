For the Cell event collapse, the Event emits a "request" to collapse from any direction.
A cell accepts and stashes the potential path (collapse request) into the many possibilities of collapable states, from all given paths.

At a point of _overflow_ the cell with yield a collapse into a preferred state (the best state given all path events) and emit this as a _potential finished cell_. All cells relative collapse until the edges of a boundry.

---

A "locked" cell should never change its state. For all incoming events The Cell will always yield the uniquely target value. The Cell may only collapse onto event paths with the target. It's likely best to _emit_ path events from locked locations (from the lowest entropy states.)

---

This divides the routine into 3 steps.

1. Identify all states for all cells, Allocate A Cell
2. Emit "Path" events through the graph
3. Cells collect paths, validate approved states and fail for bad requests.
4. Upon the highest choice entropy overflow, emit the state as a "Collapsed potential"
5. All cells within the target state should collapse neatly.

If the "collapsed potential" _layer_ does not resolve correctly, it's ignored and other layers should propogate. Upon success, all nodes of a final solution result as an overlay of finished nodes.

# A Cell

A single cell exists within the graph, existing without dependencies, accessed through the graph, and responding to Path Events with _next siblings_.

1. A List of all cells, connected to siblings.
2. All potential states of a cell.
3. All neighbours of a state for each cell.


# A Path

Once all Cells are waiting, we emit a _signal_ from an initial node. It targets every cell, gathering a path of next targets. Upon each call the path will test for validity. If the cell fails (because the path contains a _previous invalid node_), a failure kills the path.

If a cell accepts the path, the cell returns sibling cells, and all potential states. Each sibling is stepped with the same process.

As a path _walks_ the cells, if _forks_ for each new cell. When a path (a single event stepping routine) dies, its node potentials also die.


---

As an event progresses it should step to all possible targets without end - until the event is killed due to `fail()` or a cell resolves a boundry state.

The event passes through each node


