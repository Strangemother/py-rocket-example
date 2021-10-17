import client

client.background_connect()

add_node = client.add_node
add_edge = client.add_edge
update_edge = client.update_edge
update_node = client.update_node

grid=[
    [0,0,1,0,0,7,0,0,0],
    [0,0,0,0,0,0,9,8,0],
    [3,0,8,0,0,0,0,0,6],
    [1,0,0,3,0,0,5,0,0],
    [0,0,0,1,0,2,0,0,0],
    [0,0,6,0,0,5,0,0,7],
    [7,0,0,0,0,0,2,0,9],
    [0,9,3,0,0,0,0,0,0],
    [0,0,0,8,0,9,6,0,0]
]

# add_node(0)
# add_node(1)
# add_edge(0, 1, label="", background={
#     "enabled": True,
#     "color": "rgba(111,111,111,0.5)",
#     "size": 10,
#     "dashes": [20, 10],
# })

# """
# Note in this current form the update is destructive to existing properties.
# # update_edge('0-1', label='foo')
# """
# update_edge('0-1', background={'color': 'red', 'enabled':True})

entities = {}

from time import sleep
import colorsys


def main():
    send_matrix(grid)


def pause():
    sleep(.01)


def color(*a):
    """
        hue = 166 # green
        sat = 1.0
        val = 1.0
        col(hue / 360 , sat, val) == '55FF00'
    """

    v=colorsys.hsv_to_rgb(*a);
    return "".join("%02X" % round(i*255) for i in v)


def hsv_to_hex(hue, sat=1, val=1):
    return f'#{color(hue/360, sat,val)}'


def send_matrix(rows):
    """
    Connect a grid - similar to an agency matrix.
    """
    for row_i, row in enumerate(rows):
        for col, value in enumerate(row):
            _id = f'{row_i}-{col}'
            v = hsv_to_hex(166, (value+1) * .1)
            add_node(_id, value=value, color=v, label=str(value))
            pause()
            entities[_id] = value

    last_row = None

    for row_i, row_items in enumerate(rows):
        last_row_id = None

        for col, value in enumerate(row_items):
            _id = f'{row_i}-{col}'

            if last_row_id is None:
                # cannot connect nothing to here.
                last_row_id = _id
                continue

            add_edge(last_row_id, _id, arrows={'to':True})
            last_row_id = _id

            pause()
            # connect cell above this this cell.

            above_id = f'{row_i-1}-{col}'
            add_edge(above_id, _id, arrows={'to':True})
            pause()

        add_edge(f'{row_i}-0',f'{row_i+1}-0', arrows={'to':True})


if __name__ == '__main__':
    main()
