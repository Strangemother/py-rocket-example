from websocket import create_connection;
import threading
import json
import os

import atexit

stopped = threading.Event()


def main():
    background_connect()

def background_connect():
    global client
    client = connect()
    start_ticker()


def loop(): # executed in another thread
    while not stopped.wait(1): # until stopped
        ping()


def ping():
    print('.')
    v = 1
    while v:
        v = client.drain()


def start_ticker():
    t = threading.Thread(target=loop)
    t.daemon = True # stop if the program exits
    t.start()


class Client(object):
    """This client entity binds the simple connect, send, and drain to
    one address.

        c = Client(123)
        c.ensure_connect()
        c.send('text')

    once the client is prepared, calls to the server may be anonymous:

        add_node(1)
        add_node(4)
        add_edge(1,4)
    """

    connected = False
    client_id = None
    uri = 'localhost'
    port = 8000
    url = None
    ws = None

    def __init__(self, client_id=None):
        self.client_id = client_id or self.client_id
        self.url = f"ws://{self.uri}:{self.port}/ws/{client_id}"

    def ensure_connect(self):
        if self.connected:
            return

        self.ws = create_connection(self.url)
        self.connected = True
        self.announce()
        atexit.register(self.exiting)

    def exiting(self):
        self.send_json(action='exit')

    def announce(self):
        # present the client to the net.
        return self.send_json(action='wake', type='client')

    def send(self, message:str):
        return self.ws.send(message)


    def send_json(self, **kw):
        kw.setdefault('id',self.client_id)
        kw.setdefault('type','client')

        m = json.dumps(kw)
        return self.send(m)

    def drain(self):
        try:
            v = self.ws.recv()
            print('drain', v)
            return v
        except Exception as e:
            print('DRAIN ERROR', e)
            return None


def connect():
    c = Client(os.getpid())
    c.ensure_connect()
    return c


def send(m):
    return client.send(m)


def send_json(**kw):
    # m = json.dumps(kw)
    return client.send_json(**kw)


ncache = {
    'ncounter': 0,
    'ecounter': 0,

}


def add_node(_id=None, **kw):
    ncv = ncache['ncounter']

    _id = _id or kw.get('id', ncv) or ncv
    label = str(_id)
    kw.setdefault('label', label)
    kw['id'] = _id

    ncache['ncounter'] = ncv + 1

    send_json(
        type='node',
        action='add',
        value=kw,
        )
    return _id


def update_node(_id, **kw):
    send_json(
        type='node',
        action='update',
        value={**kw, 'id': _id,},
        )


def add_tab(_id=None):
    """Generatea new tab on the interface for this existing client
    """
    send_json(
        type='client',
        action='spawn',
        value=dict(),
    )


def show_tab(index=None):
    send_json(type='client',
              action='show',
              value=index, )


def hide_tab(index=None):
    send_json(
        type='client',
        action='hide',
        value=index,
    )


def remove_node(_id=None):
    send_json(
        type='node',
        action='remove',
        value=_id
        )


def update_edge(_id, **kw):
    send_json(
        type='edge',
        action='update',
        value={**kw, 'id': _id,},
        )


def add_edge(a, b, _id=None,**kw):
    """

        add_edge(0, 1, label="", background={
            "enabled": True,
            "color": "rgba(111,111,111,0.5)",
            "size": 10,
            "dashes": [20, 10],
        }
    """
    ncv = ncache['ecounter']

    _id = _id or f"{a}-{b}"
    label = kw.get('label')
    if ('label' in kw) is False:
        label = str(_id)

    ncache['ecounter'] = ncv + 1
    d = {**kw, "from": a, "to": b, 'id': _id}
    print('Send edge')
    print(d)
    send_json(
        type='edge',
        action='add',
        value=d,
        )
    return _id


def remove_edge(_id=None, b=None):

    nid = _id

    if b is not None:
        nid = f'{_id}-{b}'

    return send_json(
        type='edge',
        action='remove',
        value=nid
        )


if __name__ == '__main__':
    main()

