"""Feeds connect elements like an event listener / pusher
"""

from collections import defaultdict


connections = defaultdict(set)
references = {}
taps = defaultdict(set)
feeds = defaultdict(set)

def resolve(uuid):
    return references.get(uuid, None)


def connect(a, b, feed=None):

    ida = a.get_id()
    idb = b.get_id()
    connections[ida].add(idb)
    references[ida] = a
    references[idb] = b

    if feed is None:
        return ida, idb

    _id = feed.get_id()
    references[_id] = feed
    feeds[ida].add(_id)

    return ida, idb


def emit(event):

    _id = event['_owner']

    for uuid in connections.get(_id, ()):
        entity = resolve(uuid)
        if entity is None:
            continue

        try:
            final_event = run_taps(event)
        except DropEvent as drop_error:
            tap = drop_error.args[0]
            print('Dropped Exception:', tap.key)
            continue

        # if uuid in event.history:
        #     print('Event has met entity in the past')
        #     continue
        entity.on_feed(event)


def run_taps(event):
    """Alter the event with any waiting maps.
    """
    tap_id = event['_owner']
    for tap_uuid in taps.get(tap_id, ()):
        tap_unit = resolve(tap_uuid)
        event = tap_unit.perform(event)

    for feed_id in feeds[tap_id]:
        tap_ids = taps.get(feed_id, ())
        for t in tap_ids:
            tap_unit = resolve(t)
            event = tap_unit.perform(event)
    return event


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
        taps[id(a)].add(_id)
        references[_id] = self

    def perform(self, event):
        if self.enabled is False:
            print(f'{self.key} dropping event')
            # return DROP
            raise DropEvent(self)

        if self.passthrough:
            print(f'Sleeping Tap {self.key}')
            return event

        print(self.say)
        event.data[self.key] = True
        return event


class Event(object):

    history = None
    data = None

    def __init__(self, data, history=None):
        self.data = data or {}
        self.history = history or self.history or set()

    def set_owner(self, uuid):
        self._owner = uuid

    # def __setattr__(self, k, v):
    #     self.data[k] = v

    def __getitem__(self, k):
        return self.__dict__[k]


class FeedMixin(FeedBase):

    def emit_feed(self, data):
        """Send a feed event to feed acceptors, populating the given
        event with the owner ID
        """
        _id = self.get_id()
        # event['_owner'] = _id
        # emit(event)

        event = data

        if isinstance(event, Event) is False:
            event = Event(data)
            event.set_owner(_id)
            return emit(event)
        event.history.add(_id)
        emit(event)

    def on_feed(self, event):
        """A connected Feed called upon this unit with the given event.
        Digest the event returning nothing
        """
        # Tap here.
        owner = event._owner
        print(f'Feed to {self} from {owner}')


class Feed(FeedBase):

    # _owner = None
    def connect(self, a, b):
        # _id = self.get_id()
        ida, idb = connect(a, b, feed=self)
        self.ida = ida
        self.idb = idb


class A(FeedMixin):

    def on_feed(self, event):
        print('A recv on_feed', event)
        # self.emit_feed(event)


    def on(self):
        self.emit_feed({})


class B(FeedMixin):

    def on_feed(self, event):
        print('B recv on_feed', event)
        self.emit_feed(event)

class C(FeedMixin):

    def on_feed(self, event):
        print('C recv on_feed', event)
        # self.emit_feed(event)

a = A()
b = B()
c = C()

feed = Feed()
feed.connect(a, b)
# Feed().connect(b, c)
# Feed().connect(c, a)
# Feed().connect(c, b)

tap = Tap()
tap.connect(a)


tapb = Tap()
tapb.say = "Feed tap meddle"
tapb.key = 'monkey'
tapb.connect(feed)


# tap.passthrough = True
# tap.enabled = False
a.on()
# tapb.passthrough = True
# a.on()

