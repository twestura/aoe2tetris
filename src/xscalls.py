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

    def init_xs_state(self):
        """
        Initializes the scenario's xs state.

        Must be called in a trigger effect immediately upon the scenario's
        launch.
        """
        self._suffix += 1
        return "\n".join(
            [
                f"void _{self._suffix}() " + "{",
                "    initXsState();",
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
        the xs state is initialized.

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

    def can_render_next(self, index: int, t: Tetromino) -> str:
        """
        Returns a condition string to check if the next board at the given
        `index` should be updated to display `Tetromino` `t`.

        Parameters:
            index: One of `0`, `1`, or `2`.
            t: The value of the `Tetromino` to display.
        Raises:
            ValueError if `index` does not reprent the index of a next board.
        """
        if index not in {0, 1, 2}:
            raise ValueError(f"{index} must be `0`, `1`, or `2`.")
        return self._call_function("canRenderNext", [str(index), str(t.value)])

    def can_render_hold(self, t: Optional[Tetromino]) -> str:
        """
        Returns a condition string to check if the hold board should update to
        display the `Tetromino` `t`, or to display Invisible Objects if `t`
        is `None`.
        """
        return self._call_function(
            "canRenderHold", [str(t.value) if t else "0"]
        )

    def can_react_tetris(self) -> str:
        """Returns a condition string to check if a player scored a Tetris."""
        return self._call_function("canReactTetris")

    def can_react_move(self) -> str:
        """Returns a condition string to check if a Tetromino moved."""
        return self._call_function("canReactMove")

    def can_react_hold(self) -> str:
        """Returns a condition string to check if a Tetromino was held."""
        return self._call_function("canReactHold")

    def can_react_hold_fail(self) -> str:
        """Returns a condition string to check if a hold attempt failed."""
        return self._call_function("canReactHoldFail")

    def can_react_game_over(self) -> str:
        """Returns a condition string to react to a game being over."""
        return self._call_function("canReactGameOver")

    def can_react_game_over_easter(self) -> str:
        """
        Returns a condition string to react to play an Easter Egg sound when
        a game ends when the in-game time is over two hours.
        """
        return self._call_function("canReactGameOverEasterEgg")

    def ack_game_over_easter(self) -> str:
        """Returns an effect string to acknowledge playing the Easter egg."""
        return self._call_function("ackGameOverEasterEgg")

    def can_react_lock(self) -> str:
        """Returns a condition string to react to a Tetromino locking down."""
        return self._call_function("canReactLockdown")

    def can_explode(self, row: int) -> str:
        """
        Returns a condition string to check whether the row at index `row`
        can explode.

        Parameters:
            row: The index of the row to explode. Required to be a visible row.
        """
        return self._call_function("canExplode", [str(row)])

    def can_clear_explode(self, row: int) -> str:
        """
        Returns a condition string to check whether the row at index `row`
        can clear its explosion state.

        Parameters:
            row: The index of the row to explode. Required to be a visible row.
        """
        return self._call_function("canClearExplode", [str(row)])

    def test(self) -> str:
        """Calls a string to call a test xs functions."""
        return self._call_function("test")
