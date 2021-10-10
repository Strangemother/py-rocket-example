"""
Each cell is a self existing node, stashing and responding to layer events.
"""
from itertools import product
from itertools import cycle


def main():
    global g

    g = Grid()
    g.generate()
    return g


class Cell(object):
    """Each cell maintains is sibling and future potential states.
    """

    # All possibilities.
    possible_states = None

    # neighbours - e.g. 8, 10 or 26 directions.
    siblings = None

    #
    position = None

    def __init__(self, position, states, rules=None):
        self.position = position
        self.rules = rules or ()
        self.possible_states = states

    @property
    def xzy_id(self):
        return ''.join(map(str, self.position))

    def __repr__(self):
        return f'<Cell "{self.position}" {len(self.possible_states)} possible>'


def get_addresses(*dimensions):
    """Return a cartesian product iterable of (x,y,z) address for a grid
    of 3d points. Each address is anaolgous to a vector in space starting a (0,0,0)
    and ending in (x,y,z)
    """
    return product(*(range(x) for x in dimensions))


def cube_layers(cycles, width=3, height=3, layers=3):

    _layers = ()

    citer = cycle(cycles)

    for layer_index in range(layers):
        l = ()
        for h_i in range(height):
            row = ()
            for w_i in range(width):
                row += (next(citer),)
            l += (row, )
        _layers += (Layer(*l), )

    return Cube(*_layers)


class Cube(object):

    def __init__(self, *layers):
        self.layers = layers

    def __repr__(self):
        return f'<Cube {self.layers}>'


class Layer(object):

    def __init__(self, *rows):
        self.rows = rows

    def __repr__(self):
        return f'<Layer {self.rows}>'


class Grid(object):

    cells = None

    def __init__(self):
        self.cells = self.cells or {}#defaultdict()

    def generate(self, width=10, height=10, depth=10):
        """Generate a grid of cells. x,y,z == 10 == 1000 cells.
        """
        addresses = get_addresses(width, height, depth)

        self.make_cells(addresses)

    def make_cells(self, addresses):
        rules = self.get_rules()
        for x,y,z in addresses:
            cell = self.generate_cell((x,y,z,), rules)
            self.apply_cell(cell)

    def apply_cell(self, cell):
        self.cells[cell.xzy_id] = cell

    def generate_cell(self, position, rules):
        states = self.get_all_states(position)
        return Cell(position, states, rules)

    def get_all_states(self, position):
        """return all possible states available for the cell plus a blank cell."""
        return tuple('ABCDEF ')

    def get_rules(self):
        layers = self.get_layers()

    def get_layers(self):
        """Return many rule blocks (in 3D) to remerge into traversable graphs
        """
        return (cube_layers('A'),)


if __name__ == '__main__':
    main()
