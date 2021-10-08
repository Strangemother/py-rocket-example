from typing import List, types

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

from engine import api
from engine import system

signals = api.signals


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.message_handlers: List[types.FunctionType] = []
        self.connect_handlers: List[types.FunctionType] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        print('new client')
        for handler in self.connect_handlers:
            await handler(websocket)
        self.active_connections.append(websocket)
        await self.broadcast(f'new client: {websocket.friendly_name}', websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def bus_in(self, data):
        try:
            if data[0] == '!':
                ev = eval(data[1:])
                print('EVAL', ev)
        except Exception as e:
            print('Error:', e)
        #co_run(system.suite_enable)
        print('Eval done')

    async def broadcast(self, message: str, owner: WebSocket=None):
        await self.bus_in(message)

        for handler in self.message_handlers:
            await handler(message)

        for connection in self.active_connections:
            if connection is owner:
                continue
            await connection.send_text(message)

    def add_message_reciever(self, handler: types.FunctionType):
        print('ConnectionManager::add message handler')
        self.message_handlers.append(handler)

    def add_connection_reciever(self, receive_manager_message: types.FunctionType):
        print('ConnectionManager::add connect handler')
        self.connect_handlers.append(receive_manager_message)


manager = ConnectionManager()
core_plugins = (
    system.core.Power(),
    system.core.Power(watts_per_hour=20),
    system.core.DataNetwork(),
)

def build_system(manager):
    """Call the api for the new system, loading the initial config and
    plugins. Return a promise, with a done callback of `sys_done`.
    """
    promise = api.get_system(manager, pluggable=core_plugins)
    promise.add_done_callback(sys_done)
    return promise

import time

def sys_done(task):
    """store the task result to a global `system` variable, containing the
    newly created AdamFlightSystem
    """
    global fs
    fs = task.result()
    time.sleep(1)
    print('\nSystem mounted', fs)
    co_run(push_on_switch)


async def push_on_switch():
    await asyncio.sleep(.5)
    print('Pushing On button in 3.. 2..')
    await asyncio.sleep(1)
    await fs.suite_enable()


async def datanetwork_ready(data):
    dn = await fs.get_mounted_by_name('DataNetwork')
    # noting this is the wrong one.
    power = await fs.get_mounted_by_name('Power')
    print('datanetwork_ready event:', dn)
    print('\nAttach device to power:', dn.name, power.name)
    await dn.attach_device_to(power)
    await asyncio.sleep(.5)
    await dn.switch_on()


signals.on_sync('DataNetwork.ready', datanetwork_ready)

import asyncio


def co_run(func, *a, **kw):
    """Perform an async start of a new_sysyem, returning a promise
    """
    loop = asyncio.get_event_loop()
    co_promise = loop.create_task(func(*a, **kw))
    return co_promise


build_system(manager)


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(data, websocket)
            await manager.broadcast(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"#{client_id} left the chat")
