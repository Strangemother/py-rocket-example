from pointer import GraphPointer


class GraphNode(GraphPointer):
    """A GraphNode within the tree, storing a _thing_ and the entities personal
    ID. When walking the tree, this graphnode may react to inline events.
    """

    def __init__(self, uuid=None, entity=None):
        # self._uuid = uuid
        # self.entity = entity
        super().__init__(uuid, entity)

    def get_uuid(self):
        return self.uuid or id(self)
        # return id(self)

    def process_event_junction(self, event, junction, graph):
        print('== GraphNode process_event_junction', event, junction)
        return super().process_event_junction(event, junction, graph)
