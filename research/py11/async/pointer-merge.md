           st 3 :
            (
             (<Pointer P_49280672_1 depth=1 index=0 for op_add_10>,
              ((20,), {}),
              ((0, <N_49288384: add_all>),)),

             (<Pointer P_49280768_1 depth=1 index=1 for op_sub_5>,
              ((5,), {}),
              ((0, <N_49288384: add_all>),)),

             (<Pointer P_49280864_1 depth=1 index=2 for op_sub_6>,
              ((4,), {}),
              ((0, <N_49288384: add_all>),))
              )

With an edge, the end node doesn't present the same as other nodes
Also an edge shouldn't receive the concat params. Instead is should
receive its unique call. The _result_ is applied to the concat before
the edge node finalises.

          Na ------
    in -> Nb ------ -> out
          Nc - E0 -

The edge needs an intermediate step, called before the execution.
The value from the edge call is the result of the stash.

    ((<Pointer P_49170512_1 depth=1 index=0 for op_add_10>,
      ((20,), {}),
      ((0, <N_49177792: add_all>),)),
     (<Pointer P_49170608_1 depth=1 index=1 for op_sub_5>,
      ((5,), {}),
      ((0, <N_49177792: add_all>),)),
     (<Pointer P_49170704_1 depth=1 index=2 for op_sub_6>,
      ((4,), {}),
      ((0, <E_N_43513456__N_49177792: N_43513456__N_49177792>),)))

1. call forward any Edge types, replacing the _edge_ with the edge out node, and the value
2. This is applied to the stash
3. then merge args on destination.

This results in (as shown) 1 pointer to `add_all` with values `(20, 5, 4+e)`.
`e` is the edge operation

---

if 'merge node'
1. any edge with a merged designation is called early.
2. the result stacks into the stash
3. the pointer owning the current edge is recreate to point at the node,

*update
Therefore if 'mergenode' inspect the incoming references for the same name.
perform the early edges for that node only.
"""