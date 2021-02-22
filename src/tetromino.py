"""Represents the pieces/shapes in a game of Tetris."""


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

    @staticmethod
    def num() -> int:
        """Returns the number of Tetrominos."""
        return len(list(Tetromino))
