"""Represents the direction in which a Tetromino may face or move."""


import math
from enum import Enum
import index


class Direction(Enum):
    """Represents the direction in which a Tetromino may face or move."""

    U = 0
    R = 1
    D = 2
    L = 3

    @property
    def facing(self) -> float:
        """
        Returns the radian angle of the direction.

        The game measures angles with 0 being along the x-axis that runs
        from the western corner to the northern corner. Angles increase
        clockwise, with the y-axis running from the western corner to the
        southern corner.
        """
        return _ANGLES[self]

    @property
    def offset(self) -> index.Index:
        """Returns the offset to move one coordinate in this direction."""
        return _OFFSETS[self]


# The radian angle of the direction.
_ANGLES = {
    Direction.U: 0.75 * math.pi,
    Direction.R: 1.25 * math.pi,
    Direction.D: 1.75 * math.pi,
    Direction.L: 0.25 * math.pi,
}


# The offset point when moving one tile in a given direction.
_OFFSETS = {
    Direction.R: index.Index(0, 1),
    Direction.D: index.Index(1, 0),
    Direction.L: index.Index(0, -1),
    Direction.U: index.Index(-1, 0),
}
