"""Represents the pieces/shapes in a game of Tetris."""


from __future__ import annotations
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.units import Unit
from AoE2ScenarioParser.objects.unit_obj import UnitObject
from direction import Direction
from rotation import Rotation
from enum import Enum
from index import Index
from typing import List, Set


class Tetromino(Enum):
    """A piece in a game of Tetris."""

    L = 1
    Z = 2
    S = 3
    O = 4  # noqa: E741
    I = 5  # noqa: E741
    T = 6
    J = 7

    def __str__(self):
        return _STR[self]

    @property
    def unit(self) -> Unit:
        """Returns the unit corresponding to this Tetromino."""
        return _UNIT[self]

    @property
    def player(self) -> Player:
        """Returns the player that owns this Tetromino's unit."""
        return _PLAYER[self]

    def indices(
        self, facing: Direction = Direction.U, center: Index = None
    ) -> Set[Index]:
        """Returns the indices of this Tetromino, relative to its center."""
        if not center:
            center = Index(0, 0)
        indices = _INDICES[self]
        if self != Tetromino.O:
            if facing == Direction.R:
                indices = {index.rotate(Rotation.CW) for index in indices}
            elif facing == Direction.D:
                indices = {
                    index.rotate(Rotation.CW).rotate(Rotation.CW)
                    for index in indices
                }
            elif facing == Direction.L:
                indices = {index.rotate(Rotation.CCW) for index in indices}
        return {index + center for index in indices}

    def board_unit_ids(self, unit_board: List[List[UnitObject]]) -> Set[int]:
        """
        Returns the reference ids of units from the `unit_board` that are
        represented by this Tetromino.
        """
        return {
            unit_board[index.row][index.col].reference_id
            for index in self.indices(center=Index(1, 1))
        }

    @staticmethod
    def num() -> int:
        """Returns the number of Tetrominos."""
        return len(list(Tetromino))

    @staticmethod
    def from_int(t: int) -> Tetromino:
        """
        Returns the `Tetromino` corresponding to `int` `t`.

        Parameters:
            t: The `int` to convert.
        Raises:
            ValueError if `t` does not represent a `Tetromino`.
        """
        if t not in _FROM_INT:
            raise ValueError(f"{t} does not represent a Tetromino")
        return _FROM_INT[t]

    @staticmethod
    def init_seq() -> int:
        """Returns an int representing an initial sequence of Tetrominos."""
        return 1234567


# Maps a Tetromino to its string representation.
_STR = {
    Tetromino.I: "I",
    Tetromino.J: "J",
    Tetromino.L: "L",
    Tetromino.O: "O",
    Tetromino.S: "S",
    Tetromino.T: "T",
    Tetromino.Z: "Z",
}


# Maps a Tetromino to the unit that represents it.
_UNIT = {
    Tetromino.Z: Unit.ELITE_BERSERK,
    Tetromino.S: Unit.ELITE_EAGLE_WARRIOR,
    Tetromino.O: Unit.ELITE_JAGUAR_WARRIOR,
    Tetromino.I: Unit.ELITE_TEUTONIC_KNIGHT,
    Tetromino.T: Unit.ELITE_SAMURAI,
    Tetromino.J: Unit.ELITE_WOAD_RAIDER,
    Tetromino.L: Unit.ELITE_HUSKARL,
}


# Maps a Tetromino to the player that owns its units.
_PLAYER = {
    Tetromino.I: Player.FIVE,
    Tetromino.J: Player.SEVEN,
    Tetromino.L: Player.EIGHT,
    Tetromino.O: Player.FOUR,
    Tetromino.S: Player.THREE,
    Tetromino.T: Player.SIX,
    Tetromino.Z: Player.TWO,
}


# Maps a Tetromino to the indices relative to its center.
_INDICES = {
    Tetromino.I: {Index(0, -1), Index(0, 0), Index(0, 1), Index(0, 2)},
    Tetromino.J: {Index(-1, -1), Index(0, -1), Index(0, 0), Index(0, 1)},
    Tetromino.L: {Index(0, -1), Index(0, 0), Index(0, 1), Index(-1, 1)},
    Tetromino.O: {Index(0, 0), Index(-1, 0), Index(-1, 1), Index(0, 1)},
    Tetromino.S: {Index(0, -1), Index(0, 0), Index(-1, 0), Index(-1, 1)},
    Tetromino.T: {Index(0, -1), Index(0, 0), Index(0, 1), Index(-1, 0)},
    Tetromino.Z: {Index(-1, -1), Index(-1, 0), Index(0, 0), Index(0, 1)},
}

# Maps an integer to the Tetromino it represents.
_FROM_INT = {
    Tetromino.L.value: Tetromino.L,
    Tetromino.Z.value: Tetromino.Z,
    Tetromino.S.value: Tetromino.S,
    Tetromino.O.value: Tetromino.O,
    Tetromino.I.value: Tetromino.I,
    Tetromino.T.value: Tetromino.T,
    Tetromino.J.value: Tetromino.J,
}
