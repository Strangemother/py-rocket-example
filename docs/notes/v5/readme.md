# Events and chains.

Everything sends an 'event' into the event thread. The message is stacked into one giant async loop.

The event has an 'importance', denoting the destination disgest thread. A fast thread has no limits, running immediately and taking precendence of other threads

the secondary 'main' thread runs all main events, clocked at a standard speed. The events will run at an expected rate governed by in app properties such as "frames per second" or _hertz_ of an in-game cycled unit.

the lower loop runs all back-compute events. This should also run at an acceptable rate but the first two loops take precendence. This loop will only run during low compute or "lazy" times for cases such as background save.


---

Once an event is pushed into the digest thread, the owning element (original event emitter) may _forget_ and continue with processing.
The digest thread cares for duplicate, late and ignored events through unique ID or a quantized key.

When a message digests through the message compute functions, other _dependencies_ may have events within the same _frame_. They are popped from the frame event loop and given to the running event process.


## Conditions

Chain conditions on events, created before the event is required. Many chains compute the final value of which is applied as an event for other states to enact.

An event is applied to the digest thread when a value alters on the main state entity. If the value != the previous, an event is stacked.

Through the _frame_ many attrbuttes bind to the final event.



----


Given a list of functions and values to comput in a table, apply the variances to the event value, then select an optimum 'task' from a Decision list, choosing the highest (or lowest by option) entropy item.

E.g. An Actor has a list of achievements through a list of _decisions_. On the change of a value the Decision is dependent upon, the decision list is re-computed, choosing the next _top_ task. Once the _current_ task is finished, the new task is applied.

The Actor gains a _Current State_ to run until completion.


## Wire

A wire has two connectors and a feed pipe. Each event





