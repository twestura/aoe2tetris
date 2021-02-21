"""Represents the direction in which a Tetromino may face or move."""


from enum import Enum, auto


class Direction(Enum):
    """Represents the direction in which a Tetromino may face or move."""
    U = auto()
    R = auto()
    D = auto()
    L = auto()
