"""An object to contain the parameters for a game of Tetris."""


class TetrisParameters:
    """An instance represents values for configuring Tetris options/settings."""

    def __init__(self, num_rows: int, num_cols: int, num_visible: int):
        pass

    @property
    def num_rows(self):
        """
        Returns the number of rows on a game board.

        This value is a positive `int`.
        """
        pass  # TODO implement

    @property
    def num_cols(self):
        """
        Returns the number of columns on a game board.

        This value is a positive `int`.
        """
        pass  # TODO implement

    @property
    def num_visible(self):
        """
        Returns the number of rows visible on a game board.

        Satisfies `0 < self.num_visible < self.num_rows`.
        """
        pass  # TODO implement

    def _inv(self) -> bool:
        """Returns `True` if the class invariant is satisfied, else `False`."""
        pass
