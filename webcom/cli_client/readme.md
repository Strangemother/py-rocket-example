# client

The client tool pushes updates to the view using convenient methods for adding edges and nodes.

---

## Running

Communicate to the view through the server with a ready-to-go client.

    $> py -i client.py

This will connect to the waiting server with a cli ready for pushing updates:

```py
import client

client.background_connect()

client.add_node(0)
client.add_node(1)
client.add_edge(0, 1, label="", background={
    "enabled": True,
    "color": "rgba(111,111,111,0.5)",
    "size": 10,
    "dashes": [20, 10],
})


client.update_node(0, color='red')
"""
Note in this current form the update is destructive to existing properties.
# update_edge('0-1', label='foo')
"""
client.update_edge('0-1', background={'color': 'red', 'enabled':True})
```

### More

We can consider the client more-like an RPC, emitting tidy JSON messages through a broadcast server. The connected UI digests the messages to update an active Edge or Node list within the graph.


```py
import client

client.background_connect()
list(map(client.add_node, range(20, 30)))
```

```py
add_tab(_id=None)
show_tab(index=None)
hide_tab(index=None)

add_node(_id=None, **kw)
update_node(_id, **kw)
remove_node(_id=None)

update_edge(_id, **kw)
add_edge(a, b, _id=None,**kw)
remove_edge(_id=None, b=None)
```
