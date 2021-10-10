# Web Com

This tiny solution helps automatically push changes to a waiting graph view through a websocket implementation. Once the server is running, it may accept the UI (web view) and the optional CLI tool.

Fundamentally any message sent to the server is broadcasted to all connected clients - likely as a json formatted message.

1. Run a backend to load nodes,
2. Run a Websocket server to accept and push commands
3. A graph UI element for each node


## server

Run the `socket_server/unicorn.bat` file to run the websocket server

This runs a fastapi server through unicorn on address `http://127.0.0.1:8000`,  and websocket addresses to the same url.

## UI

Run the `ui/server.bat` to start a localhost for the UI files. They're generally one page apps to present graphs.


## CLI Client

within the CLI, run the `cli_client/main.py` or import it as a module. This consists of a few convenience tools to send graph edge and node JSON messages:

Each functional call emits a message through the background connected websocket pipe. Given the server and UI are awake, two nodes and an edge pop into view.

```py
import main

main.background_connect()

add_node = main.add_node
add_edge = main.add_edge
update_edge = main.update_edge
update_node = main.update_node

add_node(0)
add_node(1)
add_edge(0, 1, label="", background={
    "enabled": True,
    "color": "rgba(111,111,111,0.5)",
    "size": 10,
    "dashes": [20, 10],
})

"""
Note in this current form the update is destructive to existing properties.
# update_edge('0-1', label='foo')
"""
update_edge('0-1', background={'color': 'red', 'enabled':True})
```
