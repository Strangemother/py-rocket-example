

count = 10_000


class PoweredNode(object):
    name = None


classes = {}

for i in range(count):
    n = PoweredNode()
    n.name = i
    classes[i] = n
