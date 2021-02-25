"""Utilities to implement xs script calls."""


from index import Index
from variables import Variables


# TODO import somehow instead of redefining the constant
TETRIS_COLS = 10  # The number of columns in a game of tetris.


class ScriptCaller:
    """An instance manages calls to an xs script."""

    def __init__(self, variables: Variables):
        """
        Initializes a new script caller.

        Parameters:
            variables: The scenario variables with which the script calls
                can interact.
        """
        self._suffix = -1  # Increment at the start of every method.
        self._vars = variables

    def swap(self, id0: int, id1: int) -> str:
        """
        Returns a message to swap the values of variables with the given ids.

        Parameters:
            id0: the id of the first variable to swap
            id1: the id of the second variable to swap
        """
        self._suffix += 1
        return "\n".join(
            [
                f"void _{self._suffix}() " + "{",
                f"    swap({id0}, {id1});",
                "}",
            ]
        )

    def index_equals(self, index: Index, value: int) -> str:
        """
        Returns a condition string for checking if a variable equals a value.

        Parameters:
            index: the board index to check
            value: the value with which to compare
        Returns: A string message for an xs call trigger condition that calls
            a function for checking if the board tile at the given index
            as the given value.
        """
        self._suffix += 1
        c = Variables.col_variable(index.col)
        var = self._vars.board_tiles[index.row][c]
        place = c % TETRIS_COLS // 2
        return "\n".join(
            [
                f"bool _{self._suffix}() " + "{",
                f"    digitEquals({var.var_id}, {place}, {value});",
                "}",
            ]
        )

    def set_index(self, index: Index, value: int) -> str:
        """
        Returns an effect string to set the tile at index to contain value.

        Parameters:
            index: the board index to set
            value: the value to assign at index
        Returns: A string message for an xs call trigger effect that calls
            a function for setting the board tile at the given index
            to equal `value`.
        """
        self._suffix += 1
        c = Variables.col_variable(index.col)
        var = self._vars.board_tiles[index.row][c]
        place = c % TETRIS_COLS // 2
        return "\n".join(
            [
                f"void _{self._suffix}() " + "{",
                f"    setDigit({var.var_id}, {place}, {value});",
                "}",
            ]
        )

    def seq_value_equals(self, k: int, value: int) -> str:
        """
        Returns a condition string for querying the Tetromino sequence.

        Requires `k` is in `0..=6`.
        The condition passes if the `k`th element of the first Tetromino
        sequence equals `value`.
        """
        self._suffix += 1
        var = self._vars.sequences[0]
        return "\n".join(
            [
                f"void _{self._suffix}() " + "{",
                f"    digitEquals({var.var_id}, {0}, {value});",
                "}",
            ]
        )

    def swap_digits(self, tseq_index: int, i: int, j: int) -> str:
        """
        Returns an effect string to swap two digits in a sequence variable.

        Requires `i` and `j` in `0..=6`. Here `i` and `j` are the number of
        places from the right acting as indices into the number, with
        the rightmost digit at index `0`.

        Parameters:
            tseq_index: `0` or `1`, indicating if the swap should occur in
                the first or the second sequence variable.
            i: The first index to swap.
            j: The second index to swap.
        """
        self._suffix += 1
        var_id = self._vars.sequences[tseq_index].var_id
        return "\n".join(
            [
                f"void _{self._suffix}() " + "{",
                f"    swapDigits({var_id}, {i}, {j});",
                "}",
            ]
        )
