from g4.nodes.base import NodeBase

class LiveNode(NodeBase):

    def __repr__(self):
        ref = self.get_reference()
        cn = self.__class__.__name__
        return f'<{cn} "{self.get_uuid()}" {ref}>'

