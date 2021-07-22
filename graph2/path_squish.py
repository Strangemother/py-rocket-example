"""Start with the first node, and provide a ratio split of that value with the next
    Value 1 should share next (`0`) a ratio of 1 to 0
"""
path = (1, 0,
        0, 0,
        1, 5,
        2, 3,
        1, 2,
        0, 0,
        1, 5,
        2, 3,
        1, 3,
        0, 1,
        5, 2,
        3, 1,
        2, 0,
        1, 2,
        0, 0,
        1, 5,
        2, 3,
        1, 3,
        2, 2)

import random
random.seed(42)
path = tuple(random.randint(0,150) for x in range(50))
print(path)
it = iter(path)

first = path[0]
last = path[-1]
print('first = ', first)

last_v = 1
vs = ()

for i, (x, y) in enumerate(zip(it, it)):
    a, b = (1+x), (1+y)
    v = a/b
    last_v = v/last_v
    print(f"{i:<2} {a:<3} {b:<3} == {v:.4f}")#, | {last_v:.4f}")
    vs += (v, )
print(vs)

print(f'last = {last}\n')
for i, v in enumerate(reversed(vs)):
    b = last + 1
    a = b*v
    import pdb; pdb.set_trace()  # breakpoint 030043f7 //

    print(f'{i:<2}', v, a,b,)

# for i, v in enumerate(path[::2]):
#     print(i, v, path[i+1])
