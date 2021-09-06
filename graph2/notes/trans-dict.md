Transaction Machinery

To simplify the cross communication of the dict, an automated transmission across a graph of edges performs vast computational changes with one update.

Each key has a 'read', 'write', monitor. All updates set to a event queue, collected
by an event machine and pushed into a receiver.

1. build graph of nodes
2. Change value (update 'a'==1)
3. Submit SET `a` == `1` as event
4. perform step iteration
5. Tell all `a` edges, an update occured.
