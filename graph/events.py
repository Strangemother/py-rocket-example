"""An event maintains the distributed message through the tree as it traverses
the graph. For each step the event will track _history_ with optional event
hooks.


An event isn't special. Load with arguments including a unique ID, the data
and any handler functions, then push the event instance to the eventmachine
stack.

    _id = self.get_node_id(node)
    e = Event(start_id=_id, data=data, on_end=event_finished)
    events.push(event)

    def event_finished(e):
        print(e.step())
        # list of uuids.

The event will start at the _start_id_ node, bubbling through attached nodes
until the event cannot continue - or "event end".

Extend the event to be something useful, such as in-game "PowerEvent".

    class PowerEvent(Event):
        watts=1000

within your node, capture the event through GraphNode hooks.

"""

from pprint import pprint as pp
from collections import defaultdict
import queue
import time


class Event(object):
    """A single event for the dispatch machine, capturing the data and start node

    The original node does not need to be stacked; just the tree pointer and
    a reference to the original graph.
    """
    current_step = None
    clone_keys = (
        'start_id',
        'data',
        'current_step',
        #'history_hits',
        'init_id',
        'history',
        'index',
        'position_history',
        'on_each',
        'on_end',
        'unique_history',
        )

    def __init__(self, start_id, data=None, on_each=None, on_end=None):
        self.start_id = start_id
        self.data = data
        self.init_id = id(self)
        self.uuid = id(self)
        self.current_step = self.current_step or start_id
        self.history_hits = defaultdict(int)
        self.history = ()
        self.index = -1
        self.position_history = ()
        self.on_each = on_each
        self.on_end = on_end
        # Ensure the history hits of an event are unique to the clone.
        # If False, all clone events maintain the same _hits_ stack.
        self.unique_history = True

    def execute_on_each(self, action, graph):
        if callable(self.on_each):
            return self.on_each(self, action, graph)
        return action

    def execute_on_end(self, action, graph):

        if callable(self.on_end):
            return self.on_end(self, action, graph)
        print('  action:   ', action.name, action.args, action.kw)
        self.view(graph)

    def view(self, graph):
        print('* end_event.', self)

        ids = self.history + (self.current_step,)
        print('  history:  ', graph.get_entities(ids))
        print('  positions:', self.positions())
        # h = dict(self.history_hits )
        # print('  positions:', h, graph.get_entities(h))

    def steps(self):
        ids = self.history + (self.current_step,)
        return ids

    def positions(self):
        return self.position_history + (self.index,)

    def split(self, junction, action, graph):
        """Given a junction split _this_ event into X many events required
        for the continuation of the event through the graph.

        Return a tuple of cloned events, each with the new target of the
        enumerated junction.
        """
        r = ()

        for i, pointer_id in enumerate(junction):
            new_event = self.target_clone(pointer_id, i)
            r += (new_event,)
        return r

    def target_clone(self, pointer_id, index):
        """Clone this event and set the target as the given pointer ID and
        path index.

        Return the new Event.
        """
        new_event = self.clone()
        # new_event.set_target(pointer_id)
        # new_event.stash_postion(index)
        new_event.target_position(pointer_id, index)
        return new_event

    def clone(self):
        e = Event(self.start_id)
        keys = self.clone_keys

        for k in keys:
            v = getattr(self, k)
            setattr(e, k, v)
        # dv = vars(self)
        # iid = self.init_id

        if self.unique_history:
            e.history_hits = self.history_hits.copy()
        #e.__dict__.update(dv)
        return e

    def entities(self, graph=None):
        """Return a tuple of graph resolved entities for the steps of this event.
        Provide the target `graph`. If the graph is None the internal `self.graph`
        is used.
        """
        graph = graph or getattr(self, 'graph', None)
        return graph.get_entities(self.steps())

    def target_position(self, target, position):
        self.set_target(target)
        self.stash_postion(position)

    def stash_postion(self, index):
        self.position_history += (self.index, )
        self.index = index

    def set_target(self, pointer_id):
        """Set the current_step as the given pointer, ready for this event
        to recycle back into the event queue.
        """
        self.history_hits[self.current_step] += 1
        self.history += (self.current_step, )
        self.current_step = pointer_id

    def __str__(self):
        return f"<{self.__class__.__name__}({self.uuid}) from {self.start_id}>"

    def __repr__(self):
        return f'<{self.__class__.__name__}({hex(id(self.uuid))}) from {self.start_id}>'


class EventMachine(object):

    def __init__(self):
        self.stack = queue.SimpleQueue()

    def move_stepper(self, graph):
        """Perform a single step of the event machine, accepting new events
        during the execution of the _current_ steps.

        return boolean to flag if more events exist, thus another move_stepper()
        should occur. Return True if more events exist, return False if the
        event stack machine is empty.
        """
        s = self.stack
        try:
            event = s.get(False)
            # print('Perform step.', event)
            return self.execute_step(event, graph)

            # Simple queue does not track tasks.
            # s.task_done()
        except queue.Empty:
            print('Empty')
            return False

        return s.qsize() > 0

    def execute_step(self, event, graph):
        """Called by the move_stepper *knowing* an event exists.
        Perform all computations for the graph and return success

        The event keeps a start node (tree reference) and a _current step_
        tree id. For each execution the event stacks data, passing to the
        next step.

        The 'junction' is the value of the tree key "current step"
        and contains all the _next_ nodes the current node is attached.

        The list of IDS should be stacked as a junction event to the
        event machine stack.
        """
        junction = graph.get_junction(event.current_step)
        current_pointer = graph.resolve(event.current_step)

        # print(f'Execute Step "{current_pointer}" on {graph} to: {junction}')

        """The attached pointer - being the _original_ unit given to the
        graph tree - should process the junction.

        Generally the junction pointer will spawn N{len(junction)} of event
        chains to accumulate, but a pointer may offload the processing to the
        attached dataset - a potential GraphNode
        """
        action = current_pointer.process_event_junction(event, junction, graph)
        method = self.default_event_junction_action
        action = event.execute_on_each(action, graph) or action

        if action is not None:
            amap = {
                'fork': self.fork_event,
                'kill': self.end_event,
                'sleep': self.sleep_event,
            }

            method = amap.get(action.name, self.default_event_junction_action)

        return method(event, action, graph)

    def default_event_junction_action(self, event, action, graph):
        """The event did not return a known name, perform the default action
        for the event and action
        """
        print('default_event_junction_action', event, junction)

    def fork_event(self, event, action, graph):
        """Given an event, and an action to "fork" the event to all childred
        within the action 'junction', clone and emit an event for each target.

        Return a tuple of new events, applied back to the event queue.
        """
        junction = action.kw.get('junction')
        jl = len(junction)

        if jl == 0:
            print('Event has no destination')
            return self.end_event(event, action, graph)

        if jl > 0:
            print('= Fork', junction)

        if jl == 1:
            # no need to fork.
            # event.set_target(tuple(junction)[0])
            # event.stash_postion(0)
            event.target_position(tuple(junction)[0], 0)
            self.push(event)
            return (event,)

        r = event.split(junction, action, graph)
        self.push(*r)

        # r = ()

        # for i, pointer_id in enumerate(junction):
        #     new_event = event.clone()
        #     new_event.set_target(pointer_id)
        #     new_event.stash_postion(i)
        #     self.push(new_event)
        #     r += (new_event,)

        return r
        # clone the event to separate chain flows
        # append the update for each action.args[0] (junction)
        # push the updated event into the event chain
        # If required: push the _dead_ event to a void box.

    def end_event(self, event, action, graph):
        # ids = tuple(event.history.keys()) + (event.current_step,)
        event.execute_on_end(action, graph)

    def sleep_event(self, event, action, graph):
        print('= sleep', action.args)

    def push(self, *event):
        """Push an event into the event stack, ready for an incoming stepper
        event loop.

        The 'event' is any valid unit to provide through the tree.
        """
        for ev in event:
            print('Push event stack', ev)
            self.stack.put_nowait(ev)


events = EventMachine()


class TreePump(object):
    """The Event actuation for _stepping_ the event graph by one cycle, calling
    upon the _next_ set of event chain actions. In a message-step routine,
    for each graph call, subsequent step Events stack to a immediate event list,
    ready for the next step.
    """

    def drain(self):
        """Run the pump until all messages are digested
        """
        do_loop = 1
        while do_loop:
            do_loop = self.pump() is not False
            time.sleep(.01)

    def send(self, node, data=None, **kw):
        """Convert the node into a pointer ID an create a data event"""
        _id = self.get_node_id(node)
        e = Event(start_id=_id, data=data, **kw)
        return self.push_event(e)

    def push_event(self, event):
        return events.push(event)

    def pump(self):
        """Move the stepper to the next event cycle within the tree, moving the
        event index and calling upon the executable functions
        """
        return events.move_stepper(self)
