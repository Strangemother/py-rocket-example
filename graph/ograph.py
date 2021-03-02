"""An object graph is similar to a graph tree, however the _node_ in
question is associated to another node through a chained reference

    {} -> connects_to -> {}
    { animal: dog } -> has -> { legs: 4 }

This is a variation on the standard graph, where this maintains _edges_ to
each node. Each edge identifies a name and any additional compute params.

An edge name may be any value, with edges masking alternative edges (connecting
the same node)

    table   has         legs
    table   has         lamp

two nodes may connect through multiple parents:

    table   on-topof    lamp
    table   above       lamp
    table   up          lamp

"""

def main():
    pass


class OGraph(object):

    def add(entity, name=None):
        name = name or getattr(entity, 'name', id(entity))
        self.references[name] = entity

    def connect(name_a, through, name_b):
        self.relationships[through][name_a].add(name_b)
        self.relationships_rev[through][name_b].add(name_a)
