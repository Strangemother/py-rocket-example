from pprint import pprint as pp

class FindMixin(object):

    def find(self, *a, **kw):
        """Perform a graph _send_ with the standard arguments, capturing _finished_
        events into a tracking stack.

        To make this easy, a class "Structure" to capture the readback applies
        complete events to the class instance.
        """
        es = EventStack(self, *a, **kw.copy())
        kw['on_end'] = es.event_on_end
        self.send(*a, **kw)
        return es


class EventStack(object):
    """An event stack gathers updated as the event bubbles through the graph
    nodes. Find all 'complete' events captured by hook `on_end` stored to
    `self.events`.
    """

    def __init__(self, graph, *args, **kwargs):
        self.graph = graph
        self.args = args
        self.kwargs = kwargs
        self.events = ()

    def event_on_end(self, event, action, graph):
        """The given Event is complete with no more junction nodes to iterate
        Store the event to self.events and call upon any on_end hooks.
        """
        # print('event_on_end')
        event.graph = graph
        self.events += (event,)

        if 'on_end' in self.kwargs:
            self.kwargs.get('on_end')(event, action, graph)
        else:
            pp(self.chains())

    def view(self):
        """Iterprint the chains of events in the list of stored steps()
        """
        c = self.chains()
        for l in c:
            print(*l)

    def view_func_names(self):
        """Iterate the self.chains() and print a list of __name__ attributes
        of each entity. This is useful for a list of function entities.
        """
        c = self.chains()
        for l in c:
            print(*tuple(x.__name__ for x in l))

    def chains(self):
        """Iterate all the stored self.events and return the resolved entities
        for the event steps.

        Return a tuple of tuples.
        """
        ls = ()
        for e in self.events:
            # e.view(self.graph)
            l = self.graph.get_entities(e.steps())
            ls += (l,)
        return ls
