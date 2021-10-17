"""
The Event machine accepts a graph complete with edges and nodes,
and calls nodes, stepping events through connected edges.

Each 'step' of the event machine

1. The machine reads 'outputs' from nodes
2. Push the 'outputs' to the next nodes
"""
import sys
sys.path.append('F:/godot/python-rocket-software/graph3')
# import main as g3
# from g3 import Connections
import g3
from collections import defaultdict
from main import ViewConnections

class Machine(ViewConnections):

    def __init__(self, _id):#, connections):
        # self.connections = connections
        super().__init__(_id)
        self.events = defaultdict(tuple)

    def step(self):
        next_events = defaultdict(tuple)

        for key, items in self.events.items():
            # get connections of key
            # send each item to each connected unit
            if len(items) == 0:
                continue

            print('Step on', key, '==', items)
            # Call the function giving the called items
            func = self.get_attached(key)
            next_nodes = self.get_next_nodes(key)
            next_funcs = tuple(x.data for x in next_nodes)

            for value in items:
                result = func(value)
                # stack the result into the next node event stacks.
                for next_func in next_funcs:
                    next_events[next_func] += (result,)
        self.events = next_events

    def get_next_nodes(self, key):
        return self(key).next_nodes

    def get_attached(self, key):
        return self(key).data

    def input(self, key, *a, **kw):
        func = self.get_attached(key)
        self.events[key] += (func(*a, **kw),)

    # def connect(self, *units, direction=FORWARD, data=None, edge=None):
    #     for unit in units:
    #         self.events[unit] = ()
    #     return self.connect(*units, direction, data, edge)


def f_a(val):
    return val * 2

def f_b(val):
    return val + 3

def f_c(val):
    return val - 2

def f_d(val):
    return val * .5

def f_e(val):
    return val + 2

import operator as op

c=Machine(123)
# c=g3.Connections()

def m_funcs():
    c.connect(f_a, f_b, f_c)
    c.connect(f_c, f_d, )
    c.connect(f_d, f_a, )

    c.input(f_a, 10)

def m_house():
    c.connect('hallway', 'bedroom')
    c.connect('hallway', 'small-room')
    c.connect('hallway', 'bathroom')
    c.connect('hallway', 'livingroom')
    c.connect('hallway', 'kitchen')

    c.connect('bedroom', 'bed', 'pillows')
    c.connect('bed', 'blanket')
    c.connect('bedroom', 'lamp')
    c.connect('house', 'hallway')
    c.connect('hallway', 'front-door')


def m_funcs_2(g):

    def func_a(*a, **kw): print('func_a', a, kw);
    def func_b(*a, **kw): print('func_b', a, kw);
    def func_c(*a, **kw): print('func_c', a, kw);
    def func_d(*a, **kw): print('func_d', a, kw);
    def func_e(*a, **kw): print('func_e', a, kw);
    def func_f(*a, **kw): print('func_f', a, kw);
    def func_g(*a, **kw): print('func_g', a, kw);
    def func_h(*a, **kw): print('func_h', a, kw);
    def func_j(*a, **kw): print('func_j', a, kw);
    def func_k(*a, **kw): print('func_k', a, kw);
    def func_l(*a, **kw): print('func_l', a, kw);
    def func_m(*a, **kw): print('func_m', a, kw);
    def func_n(*a, **kw): print('func_n', a, kw);
    def func_o(*a, **kw): print('func_o', a, kw);
    def func_p(*a, **kw): print('func_p', a, kw);

    g.connect(
        func_a,
        func_c,
        func_e,
        func_g,
        func_h,
        func_k,
        func_l,
        func_n,
        func_o,
        func_p,
    )

    g.connect(
        func_b,
        func_d,
        func_f,
        func_g,
        func_m,
        func_o,
        func_p,
    )


    g.connect(
        func_a,
        func_d,
        func_f,
        func_l,
        func_m,
        func_n,
    )

def m_body(g):

    g.connect(
        'head',
        'neck',
        'shoulders',
        'torso',
        'legs',
        'feet',
        'toes',
        )

    g.connect('head', 'face', 'eyes')
    g.connect('head', 'ears')
    g.connect('head', 'hair')

    g.connect('face', 'nose')
    g.connect('nose', 'nostrils', 'holes')
    g.connect('face', 'mouth', 'lips')

    g.connect('torso', 'arms', 'hands', 'fingers', 'fingernails')
    g.connect('hands', 'thumbs', 'thumbnails')


def m_alphas(g):
    g.connect(*'LMONKEY')
    g.connect(*'LOTY')
    g.connect(*'LOBE')
    g.connect(*'HORSE')
    g.connect(*'HOUSE')

import string
from time import sleep

def pop_song(g):
    lines = (
        "i am the very model of a modern majorgeneral",
        "ive information vegetable animal and mineral",
        "i know the kings of england and i quote the fights historical",
        "from marathon to waterloo in order categorical",
        "im very well acquainted too with matters mathematical",
        "i understand equations both the simple and quadratical",
        "about binomial theorem im teeming with a lot o news",
        "with many cheerful facts about the square of the hypotenuse",
        "im very good at integral and differential calculus",
        "i know the scientific names of beings animalculous:",
        "in short in matters vegetable animal and mineral",
        "i am the very model of a modern majorgeneral",
        "i know our mythic history king arthurs and sir caradocs",
        "i answer hard acrostics ive a pretty taste for paradox",
        "i quote in elegiacs all the crimes of heliogabalus",
        "in conics i can floor peculiarities parabolous",
        "i can tell undoubted raphaels from gerard dows and zoffanies",
        "i know the croaking from the frogs of aristophanes",
        "then i can hum a fugue of which ive heard the musics din afore",
        "and whistle all the airs from that infernal nonsense pinafore",
        "then i can write a washing bill in babylonic cuneiform",
        "and tell you evry detail of caractacuss uniform",
        "in short in matters vegetable animal and mineral",
        "i am the very model of a modern majorgeneral",
        "in fact when i know what is meant by mamelon and ravelin",
        "when i can tell at sight a mauser rifle from a javelin",
        "when such affairs as sorties and surprises im more wary at",
        "and when i know precisely what is meant by commissariat",
        "when i have learnt what progress has been made in modern gunnery",
        "when i know more of tactics than a novice in a nunnery",
        "in short when ive a smattering of elemental strategy",
        "youll say a better majorgeneral has never sat a gee",
        "for my military knowledge though im plucky and adventury",
        "has only been brought down to the beginning of the century",
        "but still in matters vegetable animal and mineral",
        "i am the very model of a modern majorgeneral",
    )

    # g = graph.Graph(id_method=None)#id)
    last = None

    d = []

    for i, line in enumerate(lines):
        clean_line = line
        clean_line = clean_line.translate(str.maketrans('', '', string.punctuation))
        items = clean_line.lower().split(' ')
        if 'sorties' in line:
            import pdb; pdb.set_trace()  # breakpoint 747235fc //
        vv = g.connect(*items)
        sleep(1)
        if last:
            vv = g.connect(last, items[-1], color='green')
            sleep(.1)
        last = items[-1]
    return g


if __name__ == '__main__':

    pop_song(c)
