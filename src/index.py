"""An index is a coordinate on the Tetris board."""


from __future__ import annotations
from typing import Set
from rotation import Rotation


class Index:
    """An instance represents a row-column coordinate on a Tetris board."""

    def __init__(self, r: int, c: int):
        """Initializes a new index."""
        self._r = r
        self._c = c

    @property
    def row(self):
        """Returns this index's row coordinate."""
        return self._r

    @property
    def col(self):
        """Returns this index's column coordinate."""
        return self._c

    def __str__(self):
        return f'({self._row}, {self._col})'

    def __eq__(self, other):
        return (
            isinstance(other, Index)
            and self._r == other._r
            and self._c == other._c
        )

    def __hash__(self):
        return hash((self._r, self._c))

    def __ne__(self, other):
        return (
            not isinstance(other, Index)
            or self._r != other._r
            or self._c != other._c
        )

    def __add__(self, other):
        return Index(self._r + other._r, self._c + other._c)

    def rotate(self, r: Rotation) -> Index:
        """Returns an index equal to `self` rotated by the rotation."""
        return (
            Index(self._c, -self._r)
            if r == Rotation.CW else
            Index(-self._c, self._r)
        )
