
HOST = { 'system': None }


class HostSingleton(object):

    @property
    def host(self):
        return HOST['system']


class Base(HostSingleton):
    """The core util for everything
    """

    @property
    def name(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"<{self.name}>"
