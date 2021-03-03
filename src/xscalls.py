"""Interfaces between scenario triggers and the Tetris xs script."""


from typing import Optional, Sequence
from action import Action
from direction import Direction
from index import Index
from tetromino import Tetromino


SEQ_NUMS = {0, 1}  # The indices of the shuffled Tetromino sequences.


class ScriptCaller:
    """
    An instance manages calls to an xs script.

    The method `init_xs_array` must be called before any other xs function.
    All other methods raise an assertion error in a debug build if this
    method has not been called.
    """

    def __init__(self):
        """Initializes a new script caller."""
        self._suffix = -1  # Increments at the start of every method.

    def init_xs_array(self):
        """
        Initializes the scenario's xs state array.

        Must be called in a trigger effect immediately upon the scenario's
        launch.
        """
        self._suffix += 1
        return "\n".join(
            [
                f"void _{self._suffix}() " + "{",
                "    initXsArray();",
                "}",
            ]
        )

    def _call_function(
        self, name: str, params: Optional[Sequence[str]] = None
    ) -> str:
        """
        Returns a string to Call the xs script function with name `name`
        and parameters with string values given in `params`.
        Essentially calls `name(param[0], param[1], ..., param[n])`.

        Checks that self._suffix is nonnegative in order to ensure that
        the xs state array is initialized.

        Parameters:
            name: The name of the xs function in `Tetris.xs`.
            params: The parameters to pass to the function.
        Returns:
            A string for a trigger condition or effect to call the xs
            function `name` with the parameters `params`.
        """
        assert self._suffix > -1
        if not params:
            params = []
        self._suffix += 1
        return "\n".join(
            [
                f"void _{self._suffix}() " + "{",
                f"    {name}({', '.join(params)});",
                "}",
            ]
        )

    def begin_game(self):
        """
        Returns a string to call the effect of clearing and initalizing game
        state.
        """
        return self._call_function("beginGame")

    def begin_game_mid(self):
        """
        Returns a string effect message to initialize game state after
        the sequence shuffling triggers have executed.
        """
        return self._call_function("beginGameMid")

    def swap_seq_values(self, seq_num: int, i: int, j: int) -> str:
        """
        Returns a string to call the effect of swapping two values
        in the tetromino sequence.

        Parameters:
            seq_num: Either `0` or `1` to use the sequence of the first 7 or
                the second 7 Tetrominos.
            i: The first index to swap.
            j: The second index to swap.
        Raises:
            ValueError if `seq_num` is not `0` or `1` or if either `i` or `j`
                is not in `0 <= i, j <= 6`.
        """
        if seq_num not in SEQ_NUMS:
            raise ValueError(f"{seq_num} must be 0 or 1.")
        if i < 0 or i > 6:
            raise ValueError(f"{i} must satisfy 0 <= i <= 6.")
        if j < 0 or j > 6:
            raise ValueError(f"{j} must satisfy 0 <= j <= 6.")
        return self._call_function(
            "swapSeqValues", [str(x) for x in [seq_num, i, j]]
        )

    def can_render_tile(
        self, index: Index, facing: Direction, tetromino: Optional[Tetromino]
    ) -> str:
        """
        Returns a condition string for replacing a unit at a board index.


        Parameters:
            index: The row and column index of the tile.
            d: The facing direction of a piece in the tile.
            t: The piece in the tile, or `None` if the tile is unoccupied in
                the given direction.
        """
        r = str(index.row)
        c = str(index.col)
        d = str(facing.value)
        t = "0" if tetromino is None else str(tetromino.value)
        return self._call_function("canRenderTile", [r, c, d, t])

    def select_building(self, action: Optional[Action] = None) -> str:
        """Returns an effect string for setting the selected building."""
        return self._call_function(
            "selectBuilding", ["0" if action is None else str(action.value)]
        )

    def init_game_loop(self) -> str:
        """Returns an effect string to initialize game loop iteration state."""
        return self._call_function("initGameLoop")

    def can_start_new_game(self) -> str:
        """Returns a condition string to check if a new game can be started."""
        return self._call_function("canStartNewGame")

    def update(self) -> str:
        """Returns a string to call the update game state function."""
        return self._call_function("update")

    def shuffle(self) -> str:
        """
        Returns a condition string to check if the shuffle triggers should
        be activated.
        """
        return self._call_function("canGenerateSecondSequence")

    def is_game_over(self) -> str:
        """Returns a condition string to check if a game is over."""
        return self._call_function("isGameOver")

    def test(self) -> str:
        """Calls a string to call a test xs functions."""
        return self._call_function("test")
