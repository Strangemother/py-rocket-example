import client

client.background_connect()

add_node = client.add_node
add_edge = client.add_edge
update_edge = client.update_edge
update_node = client.update_node

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
