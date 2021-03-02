"""Feeds connect elements like an event listener / pusher
"""

from collections import defaultdict

class Memory(object):

    print_log = False

    def __init__(self):
        self.connections = defaultdict(set)
        self.references = {}
        self.taps = defaultdict(set)
        self.feeds = defaultdict(set)

    def resolve(self, uuid):
        return self.references.get(uuid, None)

    def connect(self, a, b, feed=None):

        ida = a.get_id()
        idb = b.get_id()
        self.connections[ida].add(idb)
        self.references[ida] = a
        self.references[idb] = b

        if feed is None:
            return ida, idb

        _id = feed.get_id()
        self.references[_id] = feed
        self.feeds[ida].add(_id)

        return ida, idb

    def log(self, *a):
        if self.print_log:
            print(*a)

    def emit(self, event):
        _id = event.owner
        self.log('Finding', _id)

        cons = self.connections.get(_id, ())

        for uuid in cons:
            entity = self.resolve(uuid)
            if entity is None:
                continue

            try:
                final_event = self.run_taps(event)
            except DropEvent as drop_error:
                tap = drop_error.args[0]
                self.log('Dropped Exception:', tap.key)
                continue

            self.log('emitting to', entity, event)
            entity.on_feed(event)
        self.log('Done', _id, cons)

    def run_taps(self, event):
        """Alter the event with any waiting maps.
        """
        tap_id = event.owner
        _taps = self.taps.get(tap_id, ())
        print('running taps for', tap_id, _taps)

        for tap_uuid in _taps:
            tap_unit = self.resolve(tap_uuid)
            event = tap_unit.perform(event)

        for feed_id in self.feeds[tap_id]:
            tap_ids = self.taps.get(feed_id, ())
            for t in tap_ids:
                tap_unit = self.resolve(t)
                event = tap_unit.perform(event)
        return event

mem = Memory()


class DropEvent(Exception):
    pass


class FeedBase(object):

    def get_id(self):
        return id(self)


class Tap(FeedBase):

    enabled = True

    passthrough = False
    say = "Tap meddled"
    key = 'meddled'

    def connect(self, a):
        _id = self.get_id()
        other_id = a.get_id()
        self.other = other_id
        mem.taps[other_id].add(_id)
        mem.references[_id] = self

    def perform(self, event):
        if self.enabled is False:
            print(f'{self.key} dropping event')
            # return DROP
            raise DropEvent(self)

        if self.passthrough:
            print(f'Sleeping Tap {self.key}')
            return event

        print(self.say.format(**self.__dict__, id=self.get_id()))
        event._data[self.key] = True
        return event


class ClassID(object):

    uuid = None

    def get_id(self):
        return self.uuid or self.__class__.__name__


class Event(ClassID):
    origin = None
    _data = None

    def __init__(self, origin, data):
        self.uuid = id(self)
        _origin = origin
        if isinstance(origin, str) is False:
            _origin = origin.get_id()
        self.origin = _origin
        self._data = data
        #print('init', origin, data)

    # def __new__(cls, owner, data):
    #     if isinstance(data, cls):
    #         print('Not new', data, data._data)
    #         return data
    #     print('New event', owner, data)
    #     return super().__new__(cls)


class FeedMixin(FeedBase):

    def emit_feed(self, event):
        """Send a feed event to feed acceptors, populating the given
        event with the owner ID
        """
        if isinstance(event, Event) is False:
            event = Event(self, event)
        _id = self.get_id()
        # event['_owner'] = _id
        event.owner = _id
        #print('Emit event', _id, event.owner, event._data)
        # time.sleep(0.8)
        mem.emit(event)

    def on_feed(self, event):
        """A connected Feed called upon this unit with the given event.
        Digest the event returning nothing
        """
        # Tap here.
        owner = event._owner
        print(f'Feed to {self} from {owner}')

import time

class Feed(FeedBase):

    # _owner = None
    def connect(self, a, b):
        # _id = self.get_id()
        ida, idb = mem.connect(a, b, feed=self)
        self.ida = ida
        self.idb = idb


class A(ClassID, FeedMixin):

    def on(self):
        print('a.on()')
        self.emit_feed({'on': True})


class Recv(ClassID, FeedMixin):

    def __init__(self, uuid=None):
        self.uuid = uuid


class B(Recv):

    def on_feed(self, event):
        uuid = self.get_id()
        print(f'{uuid} recv on_feed', event.get_id(), event._data)
        self.emit_feed(event)

class C(Recv):

    def on_feed(self, event):
        print('C recv on_feed', event, event._data)

a = A()
b = B()
c = B('C')
d = B('D')

feed = Feed()
feed.connect(a, b)
Feed().connect(b, c)
Feed().connect(c, d)

tap = Tap()
tap.connect(a)


tapb = Tap()
tapb.say = "{id} Feed tap meddle to {other}"
tapb.key = 'monkey'
tapb.connect(feed)


a.on()

# print('\nanother:')
# tap.passthrough = True
# tap.enabled = False
# # tapb.passthrough = True
# a.on()

