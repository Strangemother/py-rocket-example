from websocket import create_connection;
import threading
import json

stopped = threading.Event()


def main():
    global client
    client = connect()
    start_ticker()


def loop(): # executed in another thread
    while not stopped.wait(1): # until stopped
        ping()


def ping():
    print('.')
    client.drain()


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

    def __init__(self, client_id):
        self.client_id = client_id

        self.url = f"ws://{self.uri}:{self.port}/ws/{client_id}"

    def ensure_connect(self):
        if self.connected:
            return

        self.ws = create_connection(self.url)
        self.connected = True

    def send(self, message:str):
        return self.ws.send(message)

    def drain(self):
        v = self.ws.recv()
        print('drain', v)


def connect():
    c = Client(123)
    c.ensure_connect()
    return c


def send(m):
    return client.send(m)


def send_json(**kw):
    m = json.dumps(kw)
    return send(m)


ncache = {
    'ncounter': 0,
    'ecounter': 0,

}

def add_node(_id=None, label=None):
    ncv = ncache['ncounter']

    _id = _id or ncv
    label = label or str(_id)

    ncache['ncounter'] = ncv + 1

    send_json(
        type='node',
        action='add',
        value=dict(id=_id, label=label,),
        )
    return _id


def remove_node(_id=None):

    send_json(
        type='node',
        action='remove',
        value=_id
        )


def add_edge(a, b, _id=None, label=None):
    ncv = ncache['ecounter']

    _id = _id or f"{a}-{b}"
    label = label or str(_id)

    ncache['ecounter'] = ncv + 1

    send_json(
        type='edge',
        action='add',
        value={"from": a, "to": b, 'id': _id, 'label': label},
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
