

class Action(object):

    FORK = 'fork'

    name = None

    def __init__(self, action_name, *a, **kw):
        self.name = action_name
        self.args = a
        self.kw = kw


class GraphPointer(object):
    """A GraphPointer connects the GraphTree with the target entity, whatever
    that may be (likely a GraphNode)
    """

    def __init__(self, uuid, entity):
        self.entity = entity
        self.uuid = uuid

    def process_event_junction(self, event, junction, graph):
        """Called upon by EventMachine.execute_step() after resolving this pointer
        for the next _action_ to perform.

        The EventMachine has emit the given event through an execution process
        The 'junction' lists a range of _next_ graph keys. The junction instance may be
        any iterable type = by default a set().

        Return an action back to the event machine, signalling
        next steps. This can be done manually, but the automation will ensure
        the events are applied cleanly.

        The action.name must identify an available next step, such as
        ["fork", "kill", "sleep"].
        """

        # print('Pointer Process', junction)
        # print(' ', event.history)
        # print(' ', event.position_history)
        # graph.fork_event(event, junction)
        return Action(Action.FORK, junction=junction)

    def __str__(self):
        return f"<GraphPointer {self.uuid}: {self.entity}>"

    def __repr__(self):
        return f'<{self.__class__.__name__}({hex(id(self.uuid))}) "{self.entity}">'

