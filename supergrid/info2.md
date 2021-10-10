Considering a 9 cell grid, when collapsing a cell:

1. Grab all possibilities for the cell
2. Check the neighbours for existing nodes, and allowed siblings
3. Reduce the 'possibilities' until all neighours are questioned.

When testing a neighbour, the possibilties of the _current_ cell are chosen,
then given the _current_ cell neighours, the sibling cell offers the best relation

For example

    012
    345
    678

Given we resolve cell 5, and start at cell 0, first test `0` for _allowed_ SE
neighours. Then given the reduced set, reduce on neighours for cell 4.

1. `0` offer `A, B, C` for position `4`
2. cell `A, B, C` is tested against `1,2,3,5,6,7,8`
3. reduce any _disallowed_ given the 7 neighbours.

If a cell returns no set, the placement cannot be applied and the cell position
is invalid. The cell _recompute_ should apply. This should filter back into the
tree, recomputing all invalid nodes

