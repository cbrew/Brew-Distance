from enum import Enum
from typing import NamedTuple, Optional


def sdist(string1, string2):
    delCost = 1.0
    insCost = 1.0
    substCost = 1.0
    m = len(string1)
    n = len(string2)
    d = dict()
    d[0, 0] = 0.0
    for i in range(m):
        d[i + 1, 0] = d[i, 0] + delCost
    for j in range(n):
        d[0, j + 1] = d[0, j] + insCost
    for i in range(m):
        for j in range(n):
            if string1[i] == string2[j]:
                subst = 0
            else:
                subst = substCost
            d[i + 1, j + 1] = min(
                d[i, j] + subst, d[i + 1, j] + insCost, d[i, j + 1] + delCost
            )
    return d[m, n]


class Move(Enum):
    MATCH = 0
    INS = 1
    DEL = 2
    SUBST = 3
    INITIAL = 4


class Traceback(NamedTuple):
    cost: int
    move: Move
    traceback: Optional["Traceback"]


def edit_path(string1, string2) -> Traceback:
    len1 = len(string1)
    len2 = len(string2)
    match_cost = 0
    ins_cost = 1
    del_cost = 1
    subst_cost = 1
    initial_cost = 0
    distances = dict()
    distances[0, 0] = Traceback(cost=initial_cost, move=Move.INITIAL, traceback=None)

    # Deletions
    for i in range(0, len1):
        so_far = distances[i, 0].cost
        distances[i + 1, 0] = Traceback(
            cost=so_far + del_cost, move=Move.DEL, traceback=distances[i, 0]
        )

    # Insertions
    for j in range(0, len2):
        so_far = distances[0, j].cost
        distances[0, j + 1] = Traceback(so_far + ins_cost, Move.INS, distances[0, j])

    # Substitutions
    for i in range(0, len1):
        for j in range(0, len2):
            if string1[i] == string2[j]:
                subst = match_cost
            else:
                subst = subst_cost

            distances[i + 1, j + 1] = best(
                Traceback(subst, Move.SUBST if subst else Move.MATCH, distances[i, j]),
                Traceback(ins_cost, Move.INS, distances[i + 1, j]),
                Traceback(del_cost, Move.DEL, distances[i, j + 1]),
            )

    return extract_path(distances[len1, len2])


def extract_path(tb:Traceback):
    """
    Extract the series of operations that
    maps one string to the other.
    """
    result = []
    while tb.move != Move.INITIAL:
        result.append((tb.cost,tb.move))
        tb = tb.traceback
    ops = result[::-1]
    return ops


def best(sub_move, ins_move, del_move):
    chosen = sub_move
    if ins_move.cost < chosen.cost:
        chosen = ins_move
    if del_move.cost < chosen.cost:
        chosen = del_move
    return chosen


if __name__ == "__main__":
    print("foo", "foot", sdist("foo", "foot"))
    print("foo", "foo", sdist("foo", "foo"))
    print("foolish", "fools", sdist("foolish", "fools"))
    print("fools", "foolish", sdist("fools", "foolish"))
    print("tools", "fools", sdist("tools", "fools"))

    print("foo", "foot", edit_path("foo", "foot"))
    print("foo", "foo", edit_path("foo", "foo"))
