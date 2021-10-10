from collections import defaultdict
import sys


mapped = {}

g = defaultdict(set)
hots = defaultdict(set)
table = {}
UNUSED = -1


WORDS = ('apples',
    'window',
    'ape',
    'apex',
    'extra',
    'tracks',
    'stack',
    'yes',
    'cape',
    'cake',
    'echo',
    'win',
    # 'horse',
    # 'house',
    'wind',
    'windy',
    'w',
    'ww',
    'd' * 5,)


def main():
    global sq

    sq = Sequences(WORDS)

    ask(sq)


def ask(sequences):
    while 1:
        try:
            v = input('V:')
        except EOFError:
            sys.exit(0)

        #print(f'Reading: {len(v)}')

        for k in v:
            _hots, matches, drops = sequences.insert_keys(k) # insert_keys
            print(k, table, )
            print(', '.join(_hots), ' | ',
                ', '.join(matches), ' | ',
                ', '.join(drops))

from pprint import pprint as pp

def show():
    pp(vars(sq))

class Sequences(object):

    def __init__(self, words):
        self.hots = defaultdict(set)
        self.mapped = {}
        self.table = {}

        self.stack(words)
        self.add = self.insert_keys

    def stack(self, words):

        for w in words:
            self.input_sequence(w)

    def input_sequence(self, seq):
        """
        Add a sequence for matching
        """
        for index, item in enumerate(seq):
            next_item = seq[index]
            # Stack the _next_ of the walking tree into the set
            # of future siblings
            g[item].add(next_item)

        id_s = str(seq) #id(seq)
        # positional keep sequence
        self.mapped[id_s] = seq
        # First var hot-start
        self.hots[seq[0]].add(id_s)

        self.table[id_s] = UNUSED
        # insert_seq(id_s)

    def insert_keys(self, *chars):

        new_hots = ()
        matches = ()
        drops = ()

        #print('insert_keys', chars)
        for c in chars:
            _hots, _matches, _drops = self.insert_key(c)
            new_hots += _hots
            matches += _matches
            drops += _drops

        return new_hots, matches, drops

    def insert_key(self, char, reset_on_fail=True):
        """

        `reset_on_fail` resets the index of a sequence positon, if the
                        sequence fails the given step char.
                        If False, the sequence position is not reset, allowing
                        the contiuation of a key through misses.
        """
        res = ()
        _hots = ()
        resets = ()

        if char in self.hots:
            _hots += self.set_next_hots(char)

        for id_s, p in self.table.items():
            if p == -1: continue

            seq = self.mapped[id_s]

            try:
                index_match = seq[p] == char
            except IndexError:
                print('IndexError for', p, 'on', id_s)

                index_match = int(seq[0] == char)

            if index_match:
                self.table[id_s] += int(index_match)
                len_match = self.table[id_s] >= len(seq) #+ 1

                if len_match:
                    res += (id_s,)
                    self.table[id_s] = int(seq[0] == char)
                continue

            if reset_on_fail:
                resets += (id_s, )
                table[id_s] = -1

        return _hots, res, resets

    def set_next_hots(self, char):
        """Given a char, step the val if it exists in the 'hot start'"""
        res = ()
        _keys = self.hots.get(char)
        # print('Reading', char, _keys)
        for id_s in _keys:

            if self.table[id_s] >= 1:
                try:
                    if self.mapped[id_s][self.table[id_s]] == char:
                        continue
                except IndexError:
                    pass

            res += (id_s, )
            self.table[id_s] = 0

        return res


# def insert_keys(*chars):

#     new_hots = ()
#     matches = ()
#     drops = ()

#     #print('insert_keys', chars)
#     for c in chars:
#         _hots, _matches, _drops = insert_key(c)
#         new_hots += _hots
#         matches += _matches
#         drops += _drops

#     return new_hots, matches, drops


# def insert_key(char, reset_on_fail=True):
#     """

#     `reset_on_fail` resets the index of a sequence positon, if the
#                     sequence fails the given step char.
#                     If False, the sequence position is not reset, allowing
#                     the contiuation of a key through misses.
#     """
#     res = ()
#     _hots = ()
#     resets = ()

#     # print('Reading char', char)
#     if char in hots:
#         _hots += set_next_hots(char)

#     # print('Hots', _hots)
#     # print(table)

#     for id_s, p in table.items():
#         # The passed positions.
#         #
#         # ditched unused for speed (dependent upon the _hot start_.)
#         if p == -1: continue

#         seq = mapped[id_s]

#         try:
#             # Check if the given value matches the step position.
#             index_match = seq[p] == char
#             # print('Index', p, char, seq)
#         except IndexError:
#             # failed through the _top_; a forced finish.
#             print('IndexError for', p, 'on', id_s)

#             index_match = int(seq[0] == char)

#         if index_match:
#             # print('match', seq)
#             # Update the table; If a match, the index will update.
#             table[id_s] += int(index_match)

#             # A sequence match == the position of the stepper.
#             len_match = table[id_s] >= len(seq) #+ 1

#             if len_match:
#                 # Append to the matches set.
#                 res += (id_s,)

#                 """
#                 Reset the index position within the table.
#                 the step index may be the first char of this key, e.g "window"
#                 Thus we capture the `1` for the next expected char `i`
#                 or `0` for char `w`. If 0 the value is eventually reset to -1.
#                 on the next fail.

#                 # table[id_s] = 0
#                 # table[id_s] = -1
#                 """
#                 table[id_s] = int(seq[0] == char)

#             continue

#         # If not "avoiding hot-start", this will reset all unchanged keys to 0.
#         # With 'hot-start' the integer is left untouched as -1 for unused keys.
#         if reset_on_fail:
#             # stash to outputs.
#             resets += (id_s, )

#             """
#             Reset the table index to the inactive position, allowing _skips_
#             later.

#             #int(seq[0] == char)
#             """
#             table[id_s] = -1

#     return _hots, res, resets


# add = input_sequence
# step = insert_keys

if __name__ == '__main__':
    main()
