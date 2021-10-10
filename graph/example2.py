
from graph import GraphTree

g = GraphTree()

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


f = g.find(func_e)

g.drain()
f.view_func_names()

def main():
    pass



if __name__ == '__main__':
    main()
