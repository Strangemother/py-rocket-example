from collections import defaultdict
import sys

import sys

from pprint import pprint as pp


mapped = {}

g = defaultdict(set)
# hots = defaultdict(set)
# table = {}
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
    sq = Sequences(WORDS)
    ask_loop(sq)
    return sq


def ask_loop(sequences):
    while 1:
        try:
            ask_inject(sequences)
        except (EOFError, KeyboardInterrupt) as e:
            print('Close ask-loop')
            return

    return sequences


def ask_inject(sequences):
    v = input('?: ')
    r = single_frames(sequences, v)
    # r = mass_frame(sequences, v)
    print(r)


def single_frames(sequences, iterable):
    """ Push many chars into the sequence and render many single frames,
    returning the last (current) result from the iteration

    Functionally, this affects the sequence table in the same manner as "mass_frame"
    but yields _the last_ result:

        ?: window
        # ... 5 more frames.

        WORD    POS  | NEXT | STRT | OPEN | HIT  | DROP
        apples       |      |      |      |      |
        window   1   |  i   |      |  #   |  #   |
        ape          |      |      |      |      |
        apex         |      |      |      |      |
        extra        |      |      |      |      |
        tracks       |      |      |      |      |
        stack        |      |      |      |      |
        yes          |      |      |      |      |
        cape         |      |      |      |      |
        cake         |      |      |      |      |
        echo         |      |      |      |      |
        win      1   |  i   |  #   |  #   |      |
        wind     1   |  i   |  #   |  #   |      |
        windy    1   |  i   |  #   |  #   |      |
        w        1   |      |  #   |  #   |  #   |
        ww       1   |  w   |  #   |  #   |      |
        ddddd        |      |      |      |      |

          (
            ('win', 'ww', 'wind', 'w', 'windy'),
            ('window', 'w'),
            ()
          )
    """
    return sequences.table_insert_keys(iterable)


def mass_frame(sequences, iterable):
    """
    Push many chars into the sequence and return a concat of all starts, hits,
    and drops for the iterable.

        ?: window

        WORD    POS  | NEXT | STRT | OPEN | HIT  | DROP
        apples       |      |      |      |      |
        window   1   |  i   |  #   |  #   |  #   |
        ape          |      |      |      |      |
        apex         |      |      |      |      |
        extra        |      |      |      |      |
        tracks       |      |      |      |      |
        stack        |      |      |      |      |
        yes          |      |      |      |      |
        cape         |      |      |      |      |
        cake         |      |      |      |      |
        echo         |      |      |      |      |
        win      1   |  i   |  #   |  #   |  #   |  #
        wind     1   |  i   |  #   |  #   |  #   |  #
        windy    1   |  i   |  #   |  #   |      |  #
        w        1   |      |  #   |  #   |  #   |  #
        ww       1   |  w   |  #   |  #   |      |  #
        ddddd        |      |  #   |      |      |  #

        ( ('ww', 'windy', 'win', 'wind', 'w', 'window', 'ddddd', 'ww', 'windy',
            'win', 'wind', 'w'),
          ('w', 'win', 'wind', 'window', 'w'),
          ('w', 'ww', 'win', 'wind', 'windy', 'ddddd')
        )

    This is useful for mass framing:

        V:apextrackstackcapechoappleswwindowwindyyescakedddddf
        IndexError for 1 on w
        IndexError for 1 on w

          WORD    POS  | NEXT | STRT | OPEN | HIT  | DROP
          apples       |      |  #   |      |  #   |  #
          window       |      |  #   |      |  #   |  #
          ape          |      |  #   |      |  #   |  #
          apex         |      |  #   |      |  #   |  #
          extra        |      |  #   |      |  #   |  #
          tracks       |      |  #   |      |  #   |  #
          stack        |      |  #   |      |  #   |  #
          yes          |      |  #   |      |  #   |  #
          cape         |      |  #   |      |  #   |  #
          cake         |      |  #   |      |  #   |  #
          echo         |      |  #   |      |  #   |  #
          win          |      |  #   |      |  #   |  #
          wind         |      |  #   |      |  #   |  #
          windy        |      |  #   |      |  #   |  #
          w            |      |  #   |      |  #   |  #
          ww           |      |  #   |      |  #   |  #
          ddddd        |      |  #   |      |  #   |  #
    """
    trip = sequences.insert_keys(*iterable)
    sequences.print_state_table(*trip)
    return trip




def pr(*a):
    print(' '.join(a))


def bool_pr(key, items, true='+'):
    # return ['', true][key in items]
    return str_bool(key in items, true)

def str_bool(val, true='+'):
    return ['', true][val]


def show():
    pp(vars(sq))


class Sequences(object):

    def __init__(self, words=None, data=None):

        if data is None:
            data = {
                'hots': defaultdict(set),
                'mapped': {},
                'table': {},
                'graph': defaultdict(set),
            }

        self.set_data(data)
        if words is not None:
            self.stack(words)

        self.add = self.insert_keys

    def get_data(self):
        return {
            'hots': self.hots,
            'mapped': self.mapped,
            'table': self.table,
            'graph': self.graph,
        }

    def set_data(self, *data):
        self.__dict__.update(*data)

    def stack(self, words):
        for w in words:
            self.input_sequence(w)

    def table_insert_keys(self, chars):

        ml = 4
        lines = ()
        spacer = None# ['',] * (len(header) + 1)
        header = ('WORD', 'POS', 'NEXT', 'START', 'OPEN', 'MATCH', 'DROP', )
        res = None
        for k in chars:
            lines += ( spacer, header, )
            # _hots, matches, drops
            res = self.insert_keys(k) # insert_keys
            self.print_insert_table(k, *res)# _hots, matches, drops)
        return res

    def input_sequence(self, seq):
        """
        Add a sequence for matching
        """
        for index, item in enumerate(seq):
            next_item = seq[index]
            # Stack the _next_ of the walking tree into the set
            # of future siblings
            self.graph[item].add(next_item)

        id_s = str(seq) # str(seq) #id(seq)
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
        matches = ()
        _hots = ()
        resets = ()
        target = self.table

        if char in self.hots:
            _hots += self.set_next_hots(char)

        for id_s, p in target.items():
            if p == -1: continue

            seq = self.mapped[id_s]

            try:
                index_match = seq[p] == char
            except IndexError:
                print('IndexError for', p, 'on', id_s)
                index_match = int(seq[0] == char)

            if index_match:
                target[id_s] += int(index_match)
                len_match = target[id_s] >= len(seq)
                if len_match:
                    matches += (id_s,)
                    target[id_s] = int(seq[0] == char)
                continue

            if reset_on_fail:
                resets += (id_s, )
                target[id_s] = -1

        return _hots, matches, resets

    def set_next_hots(self, char):
        """Given a char, step the val if it exists in the 'hot start'"""
        res = ()
        _keys = self.hots.get(char)
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

    def print_state_table(self, hots=None, matches=None, drops=None):
        """print a table of the current state, inject hots, matches or drops
        to highlight within the table.

            self.print_state_table('ape',('ww', 'echo','w', ), 'yeswno' )

        """
        hots = hots or ()
        matches = matches or ()
        drops = drops or ()

        return self.print_insert_table(None, hots, matches, drops)

    def print_insert_table(self, char, _hots, matches, drops):
        opens = ()
        lines = ()
        ml = 4
        spacer = None
        header = ('WORD', 'POS', 'NEXT', 'STRT', 'OPEN', 'HIT', 'DROP', )
        lines += ( spacer, header, )
        for tk, v in self.table.items():
            # if v < 0:
            #     continue
            ml = max(ml, len(tk)+1)
            opens += ( (tk,v,), )
            _next = '' # tk[0]
            if v > -1:
                try:
                    _next = tk[v]# if v > -1 else 0]
                except IndexError:
                    pass

            line = (
                    tk,
                    v if v > -1 else '',
                    _next,
                    bool_pr(tk, _hots, '#'),# 'started'),
                    str_bool(v > -1, '#'),# 'open'),
                    bool_pr(tk, matches, '#'),# 'match'),
                    bool_pr(tk, drops, '#'),# 'dropped'),
                )

            lines += ( line, )

        # print(k, sequences.table, )
        # print(', '.join(_hots), ' | ',
        #     ', '.join(matches), ' | ',
        #     ', '.join(drops))
        print_table(lines, ml)

    def add_to(self, entity, other):
        return entity.table_insert_keys(other)

    def __iadd__(self, other):
        """Edit the sequences _in place_, mutating the current sequence.
        """
        self.add_to(self, other)
        return self

    def __add__(self, other):
        """Alter a new one (somehow.)
        """
        entity = self.__class__(data=self.get_data())
        self.add_to(entity, other)
        return entity



def print_table(lines, ml):
    for l in lines:
        if l is None:
            print('')
            continue

        pr(f"  {l[0]:<{ml}} {l[1]:^4} | {l[2]:^4} | {l[3]:^4} | {l[4]:^4} | {l[5]:^4} | {l[6]:^4}")


if __name__ == '__main__':
    r = main()
