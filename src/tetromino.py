"""Represents the pieces/shapes in a game of Tetris."""


from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.units import Unit
from direction import Direction
from rotation import Rotation
from enum import Enum, auto
from index import Index
from typing import Set


class Tetromino(Enum):
    """A piece in a game of Tetris."""
    I = auto()
    J = auto()
    L = auto()
    O = auto()
    S = auto()
    T = auto()
    Z = auto()

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

    @property
    def indices(
            self,
            facing: Direction=Direction.U,
            center: Index=None) -> Set[Index]:
        """Returns the indices of this Tetromino, relative to its center."""
        if not center:
            center = Index(0, 0)
        indices = _INDICES[self]
        if self != Tetromino.O:
            if facing == Direction.R:
                indices = { index.rotate(Rotation.CW) for index in indices }
            elif facing == Direction.D:
                indices = {
                    index.rotate(Rotation.CW).rotate(Rotation.CW)
                    for index in indices
                }
            elif facing == Direction.L:
                indices = { index.rotate(Rotation.CCW) for index in indices }
        return {index + center for index in indices}

    @staticmethod
    def num() -> int:
        """Returns the number of Tetrominos."""
        return len(list(Tetromino))


# Maps a Tetromino to its string representation.
_STR = {
    Tetromino.I : 'I',
    Tetromino.J : 'J',
    Tetromino.L : 'L',
    Tetromino.O : 'O',
    Tetromino.S : 'S',
    Tetromino.T : 'T',
    Tetromino.Z : 'Z',
}


# Maps a Tetromino to the unit that represents it.
_UNIT = {
    Tetromino.Z : Unit.ELITE_BERSERK,
    Tetromino.S : Unit.ELITE_HUSKARL,
    Tetromino.O : Unit.ELITE_THROWING_AXEMAN,
    Tetromino.I : Unit.ELITE_TEUTONIC_KNIGHT,
    Tetromino.T : Unit.ELITE_SAMURAI,
    Tetromino.J : Unit.ELITE_WOAD_RAIDER,
    Tetromino.L : Unit.ELITE_LONGBOWMAN,
}


# Maps a Tetromino to the player that owns its units.
_PLAYER = {
    Tetromino.I : Player.FIVE,
    Tetromino.J : Player.SEVEN,
    Tetromino.L : Player.EIGHT,
    Tetromino.O : Player.FOUR,
    Tetromino.S : Player.THREE,
    Tetromino.T : Player.SIX,
    Tetromino.Z : Player.TWO,
}


# Maps a Tetromino to the indices relative to its center.
_INDICES = {
    Tetromino.I : {Index(0, -1), Index(0, 0), Index(0, 1), Index(0, 2)},
    Tetromino.J : {Index(-1, -1), Index(0, -1), Index(0, 0), Index(0, 1)},
    Tetromino.L : {Index(0, -1), Index(0, 0), Index(0, 1), Index(-1, 1)},
    Tetromino.O : {Index(0, 0), Index(-1, 0), Index(-1, 1), Index(0, 1)},
    Tetromino.S : {Index(0, -1), Index(0, 0), Index(-1, 0), Index(-1, 1)},
    Tetromino.T : {Index(0, -1), Index(0, 0), Index(0, 1), Index(-1, 0)},
    Tetromino.Z : {Index(-1, -1), Index(-1, 0), Index(0, 0), Index(0, 1)},
}
