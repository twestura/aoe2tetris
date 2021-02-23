"""Represents the direction in which a Tetromino may face or move."""


from enum import Enum, auto


class Direction(Enum):
    """Represents the direction in which a Tetromino may face or move."""
    U = auto()
    R = auto()
    D = auto()
    L = auto()


# TODO map to facet/rotation for setting unit direction
# can that even be replaced?
# would then need 4 sets of Invisible objects...
