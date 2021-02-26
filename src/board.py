"""A board for playing a game of Tetris."""


from AoE2ScenarioParser.objects.unit_obj import UnitObject
from direction import Direction
from index import Index
from typing import Dict, Generator, List, Optional


# A tile on the game board.
Tile = Dict[Direction, UnitObject]


class Board:
    """An instance represents a single game's board."""

    def __init__(self, r: int, c: int, v: int):
        """
        Initializes a new `r`-by-`c` Tetris board.

        Parameters:
            r: the number of rows
            c: the number of columns
            v: the row-index of the first visible row
        """
        self._r = r
        self._c = c
        self._v = v
        self._tiles: List[List[Optional[Tile]]] = [
            [{} for __ in range(self._c)] for __ in range(self._r)
        ]

    @property
    def num_rows(self) -> int:
        """Returns the number of rows in this Tetris board."""
        return self._r

    @property
    def num_cols(self) -> int:
        """Returns the number of columns in this Tetris board."""
        return self._c

    @property
    def visible_start(self) -> int:
        """Returns the row index of this `Board`'s first visible row."""
        return self._v

    def __getitem__(self, index: Index) -> Optional[Tile]:
        return self._tiles[index.row][index.col]

    def is_in_bounds(self, index: Index) -> bool:
        """Returns `True` if `index` is inside of the game board."""
        return 0 <= index.row < self._r and 0 <= index.col < self._c

    def is_visible(self, index: Index) -> bool:
        """
        Returns whether the tile at `index` is in the visible part of the board.
        """
        return self.is_in_bounds(index) and index.row >= self._v

    def visible(self) -> Generator[Tile, None, None]:
        """Yields the visible `Tile`s of this `Board`."""
        for r in range(self._v, self._r):
            for c in range(self._c):
                # All visible tiles are not `None`.
                yield self._tiles[r][c]  # type: ignore
