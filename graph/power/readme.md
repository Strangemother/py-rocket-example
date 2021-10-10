# Power and Energy

The power chain provides a simulated energy flow for devices within the graphed nodes.

A node _accepts_ or _dispatches_ energy, presented through the graph chain events
as an anonymous event. Every entity within the event chain may _pass_ or _digest_ the event content, namely a power value to manipulate before bubbling. The event distribution manifests as single message events, sent to each node within the event forward walk.

Notably this may hinder the event chain as the "EventMachine" runs at FPS. If the interface is running at 60fps, a power event through > 60 entities will take over a second. As such an 'immediate' tree should capture power nodes. The application will graph this tree independently of the entire system graph.
