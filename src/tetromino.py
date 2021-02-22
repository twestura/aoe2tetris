"""Represents the pieces/shapes in a game of Tetris."""


from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.units import Unit
from enum import Enum, auto


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
        return {
            Tetromino.I : 'I',
            Tetromino.J : 'J',
            Tetromino.L : 'L',
            Tetromino.O : 'O',
            Tetromino.S : 'S',
            Tetromino.T : 'T',
            Tetromino.Z : 'Z',
        }[self]

    @property
    def unit(self) -> Unit:
        """Returns the unit corresponding to this Tetromino."""
        return {
            Tetromino.Z : Unit.ELITE_BERSERK,
            Tetromino.S : Unit.ELITE_HUSKARL,
            Tetromino.O : Unit.ELITE_THROWING_AXEMAN,
            Tetromino.I : Unit.ELITE_TEUTONIC_KNIGHT,
            Tetromino.T : Unit.ELITE_SAMURAI,
            Tetromino.J : Unit.ELITE_WOAD_RAIDER,
            Tetromino.L : Unit.ELITE_LONGBOWMAN,
        }[self]

    @property
    def player(self) -> Player:
        """Returns the player that owns this Tetromino's unit."""
        return {
            Tetromino.I : Player.FIVE,
            Tetromino.J : Player.SEVEN,
            Tetromino.L : Player.EIGHT,
            Tetromino.O : Player.FOUR,
            Tetromino.S : Player.THREE,
            Tetromino.T : Player.SIX,
            Tetromino.Z : Player.TWO,
        }[self]

    @staticmethod
    def num() -> int:
        """Returns the number of Tetrominos."""
        return len(list(Tetromino))
