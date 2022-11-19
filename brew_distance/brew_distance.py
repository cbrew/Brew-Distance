"""Calculate the weighted edit distance of two strings."""

# pylint: disable=superfluous-parens, too-many-locals, too-many-boolean-expressions

# Copyright (C) 2017, 2018 David H. Gutteridge.
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.

from collections import namedtuple
import numbers
import sys

# Public symbols
__all__ = ("distance", "BrewDistanceException")
__author__ = "David H. Gutteridge and Chris Brew"
__version__ = "1.0.2"

from dataclasses import dataclass

from enum import Enum
from typing import List, Optional, NamedTuple, Union, Tuple


class BrewDistanceException(Exception):
    """Brew-Distance-specific exception used with argument validation."""

    pass


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


def _best(sub_move: Traceback, ins_move: Traceback, del_move: Traceback):
    """Determine the optimum edit."""

    (increment, move1, traceback1) = sub_move
    cost_with_sub = increment + traceback1.cost

    (increment, move2, traceback2) = ins_move
    cost_with_ins = increment + traceback2.cost

    (increment, move3, traceback3) = del_move
    cost_with_del = increment + traceback3.cost

    best_cost = cost_with_sub
    move = move1
    traceback = traceback1

    if cost_with_ins < best_cost:
        best_cost = cost_with_ins
        move = move2
        traceback = traceback2

    if cost_with_del < best_cost:
        best_cost = cost_with_del
        move = move3
        traceback = traceback3

    # This is predicated on match having a lower cost than other
    # operations, and so doesn't necessarily work if that doesn't hold.
    if best_cost == traceback.cost:
        move = Move.MATCH

    return Traceback(best_cost, move, traceback)


def _edit_path(string1, string2, cost) -> Traceback:
    """Determine the transformations required to make the first string the same as the second."""
    len1 = len(string1)
    len2 = len(string2)
    (match_cost, ins_cost, del_cost, subst_cost,initial_cost) = (cost[m] for m in Move)
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

            distances[i + 1, j + 1] = _best(
                Traceback(subst, Move.SUBST if subst else Move.MATCH, distances[i, j]),
                Traceback(ins_cost, Move.INS, distances[i + 1, j]),
                Traceback(del_cost, Move.DEL, distances[i, j + 1]),
            )

    return distances[len1, len2]


def _list_edits(raw_edits: Traceback) -> List[Move]:
    """Create a list of the edits made."""
    just_edits = list()

    # (We don't bother reporting the initial match, as that's pointless.)
    while raw_edits.traceback is not None:
        just_edits.insert(0, raw_edits.move)
        raw_edits = raw_edits.traceback

    return just_edits


def distance(
    string1: str,
    string2: str,
    output="both",
    cost={Move.MATCH: 0, Move.INS: 1, Move.DEL: 1, Move.SUBST: 1, Move.INITIAL:0},
) -> Union[int, List[Move], Tuple[int, List[Move]]]:
    """Determine the weighted edit distance between two strings.

    string1 is the string to be transformed.

    string2 is the transformation target.

    Optional output is a string containing "distance", "edits", or
    "both", which determine results output, see below.

    Optional cost is a four element tuple of numbers used to adjust
    the costs of matches, insertions, deletions, and substitutions.
    (It is not recommended that match costs be adjusted: the algorithm
    is predicated on match having a lower cost than other operations.)

    The results vary depending on the output option:
        "distance": provides the edit distance as a number.
        "edits": provides an array with the list of edit actions.
        "both: provides a tuple containing the output of both
        previous options.
    """
    if not isinstance(string1, str) or not isinstance(string2, str):
        raise BrewDistanceException("Brew-Distance: non-string input supplied.")

    if output != "both" and output != "distance" and output != "edits":
        raise BrewDistanceException("Brew-Distance: invalid output parameter supplied.")
    elif (
        not isinstance(cost[Move.MATCH], numbers.Real)
        or not isinstance(cost[Move.INS], numbers.Real)
        or not isinstance(cost[Move.DEL], numbers.Real)
        or not isinstance(cost[Move.SUBST], numbers.Real)
    ):
        raise BrewDistanceException("Brew-Distance: invalid cost parameter supplied.")
    else:
        results = _edit_path(string1, string2, cost)

        if output == "distance":
            return results[0]
        elif output == "edits":
            return _list_edits(results)
        else:
            return (results[0], _list_edits(results))


if __name__ == "__main__":
    print("Brew-Distance: determining results for 'foo' vs. 'fou':")
    print(str(distance("foo", "fou", "both")))

