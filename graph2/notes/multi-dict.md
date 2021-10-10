# Faceted Dictionary

The multi-faced dictionary (Tree) binds chainmaps through connections, with each node
containing _root_ dictionary and a directional dictionary. when resolving a dictionary map,
the result will contain the node data, and the dictionaries between the two resolved nodes.

    A = {foo:1}
    B = {bar:2}

+ get A
+ get B

    d['A']
    d.get('A')

+ get a through b: A AB B

    d.get_through('A', 'B')

This should work through any direction facet

    # A AU U
    d.get_through('A', 'U')

    # A AB B BC C CD ...
    d.get_through('ABCDEF')

+ get B through A

+ get A to C through AB B BC

+ get C up to A though C CB B BA A as one command.

---

Forward is not reverse

For all references within the documentation, we've discussed _one direction_ whilst walking the facets. This means for every chain call, we've asked for a dict list in the _forward_ direction. Although we can resolve through a backward direction "B => A", this resolves a chain of directionality "B -> BA -> A" in a forward direction from _A_.

The two _walks_ across the 2 nodes act directionality on the `2n` facet.

              1n   2n    3n
    A => B == A -> AB -> B
    B => A == B -> BA -> A

`AB` can be the same entity as `BA` for a unidirectional facet.

As an analogy. Consider each node `A`|`B` as tiles to step upon. When stepping from A to B, you point towards B and step. When moving from tile B to A, you perform a 180 degree rotation, and step _forward_ onto tile B.  You've performed two forward steps from two different origin points.

---

The _reverse_ of `AB` is not the "BA" noted above.  When stepping the _reverse_ direction from A to B, the `2n` facet will not yield the same `2n(AB)` as above, but rather a dictionary representing `¬2n(AB)`.

> Introducing "not" `¬` to identify _reverse_ of a walk, we `A` means walk forward and `¬A` to walk and resolve the negative steps of the same walk.


                1n    2n    3n
     A => B  == A ->  AB -> B
     A ¬> B  == A -> ¬AB -> B

Here we identify the initial step `¬A` in reverse, resolving to `B` but B does not own the "not" `¬` operator. We could also state `¬A => B` or even `A ¬=> B`, as they would resolve the same entities though each facet, however the _faces_ of the facet `A`|`B` don't maintain a directionality (it has one dict), therefore resolving a _face_ `A` from any outer facet will yield the same result.

As an analogy, consider the faces `A` and `B` as locations on a map for a race, with `AB` as the _normal route_, and `¬AB` as the route whilst walking backward. They both yield the same finish line, but the backward racer may opt for an different route, and as such collect alternative checkpoints.

---

Another useful analogy may be an infinite line of numbers. Our initial point `A` rests at `0` and `B` is at `1`. Whilst on `B` we start relatively and assume point `0`, and the next is `A` == `1`. We can forward to `0 + 1` but to resolve backward we must negate with `-1`.

For the Faces of the facet, they always resolve to _one resolution_. the edges will resolve directionally different values; `A->B`, `B->A`, `A¬>B`, `B¬A`
