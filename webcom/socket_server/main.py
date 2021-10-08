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


import asyncio


class Manager(object):
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def send_personal_message(self, data, websocket):
        await websocket.send_text('thanks')

    async def broadcast(self, message: str, owner: WebSocket=None):
        for connection in self.active_connections:
            if connection is owner:
                continue
            await connection.send_text(message)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)


def co_run(func, *a, **kw):
    """Perform an async start of a new_sysyem, returning a promise
    """
    loop = asyncio.get_event_loop()
    co_promise = loop.create_task(func(*a, **kw))
    return co_promise


@app.get("/")
async def get():
    return HTMLResponse(html)

manager = Manager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print('>', data)
            await manager.send_personal_message(data, websocket)
            await manager.broadcast(data, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"#{client_id} left the chat")
