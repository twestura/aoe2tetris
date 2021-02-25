"""Container for the variables used in a scenario."""

from AoE2ScenarioParser.objects.triggers_obj import TriggerObject as TMgr
from AoE2ScenarioParser.objects.variable_obj import VariableObject as Var
from typing import List, Tuple
from direction import Direction
from tetromino import Tetromino


# TODO import these somehow instead of redefining the constants
TETRIS_ROWS = 40  # The number of rows in a game of tetris.
TETRIS_COLS = 10  # The number of columns in a game of tetris.
NUM_VISIBLE = 20  # The number of visible rows in the Board.
INIT_ROW = 19  # One row above the first visible row.
INIT_COL = 4  # Left-center column.


class ScnVar:
    """An instance represents a variable object and its initial value."""

    def __init__(self, tmgr: TMgr, name: str, init: int):
        """Initializes a new Variable with the given name and initial value."""
        self._var = tmgr.add_variable(name)
        self._init = init

    @property
    def var(self) -> Var:
        """Returns the variable object used for this var in the scenario."""
        return self._var

    @property
    def init(self) -> int:
        """Returns this variable's initial value."""
        return self._init

    @property
    def var_id(self) -> int:
        """Returns this variable's id number."""
        return self._var.variable_id

    @property
    def name(self) -> str:
        """Returns the name of this variable."""
        return self._var.name


def _declare_seq_variables(tmgr: TMgr) -> Tuple[ScnVar, ScnVar]:
    """
    Returns a pair of variables for holding Tetromino sequences.

    The first index holds the first seven Tetrominos, and the second index
    holds the final seven Tetrominos.
    """
    return (
        ScnVar(tmgr, "seq0", Tetromino.init_seq()),
        ScnVar(tmgr, "seq1", Tetromino.init_seq()),
    )


def _declare_board_variables(tmgr: TMgr) -> List[List[ScnVar]]:
    """
    Returns a 2d list of variables representing the state of the game board.

    Each variable is a 5 digit number, with each digit in `0..=4`.
    Column `0` is the least significant digit of the first value,
    and column `5` is the least significant digit of the second value.
    """
    return [
        [
            ScnVar(tmgr, f"Board[{r}][0..5]", 0),
            ScnVar(tmgr, f"Board[{r}][5..10]", 0),
        ]
        for r in range(TETRIS_ROWS)
    ]


class Variables:
    """An instance represents the variables used in a scenario."""

    def __init__(self, tmgr: TMgr):
        """
        Assigns variables to the scenario whose triggers are managed by `tmgr`.

        Parameters:
            tmgr: A scenario's trigger manager.
        """
        self._score = ScnVar(tmgr, "Score", 0)
        self._selected = ScnVar(tmgr, "Selected Building", 0)
        self._sequences = _declare_seq_variables(tmgr)
        self._seq_index = ScnVar(tmgr, "Current Tetromino Index", 0)
        self._facing = ScnVar(tmgr, "Facing", Direction.U.value)
        self._row = ScnVar(tmgr, "Row Index", INIT_ROW)
        self._col = ScnVar(tmgr, "Col Index", INIT_COL)
        self._board_tiles = _declare_board_variables(tmgr)

    @property
    def score(self) -> ScnVar:
        """
        Returns a variable for the player's Tetris score.

        The score is a nonnegative `int`.
        """
        return self._score

    @property
    def selected(self) -> ScnVar:
        """
        Returns a variable for the player's select building.

        The variable's value represents the action corresponding to the
        selected building. The variable is set to 0 when no building
        is selected for the current game tick.
        """
        return self._selected

    @property
    def sequences(self) -> Tuple[ScnVar, ScnVar]:
        """
        Returns a tuple of scenario variables for holding Tetromino sequences.

        The first variable represents the first seven Tetrominos,
        and the second variable represents the final seven Tetrominos.
        """
        return self._sequences

    @property
    def seq_index(self) -> ScnVar:
        """
        Returns a variable containing the index in the Tetromino sequence.

        The Variable's value indicates the currently active Tetromino and
        must be in the range `0..Tetromino.num()`.
        """
        return self._seq_index

    @property
    def facing(self) -> ScnVar:
        """
        Returns a variable to represent the active Tetromino's facing direction.

        The values of the variable correspond to the values of the
        Direction Enum.
        """
        return self._facing

    @property
    def row(self) -> ScnVar:
        """
        Returns a variable containing the active Tetromino's row index.

        The variable's value is in `0..NUM_ROWS`.
        """
        return self._row

    @property
    def col(self) -> ScnVar:
        """
        Returns a variable containing the active Tetromino's col index.

        The variable's value is in `0..NUM_COLS`.
        """
        return self._col

    @property
    def board_tiles(self) -> List[List[ScnVar]]:
        """
        Returns a 2d list of variables representing the board state.

        The outer list has an entry for each row.
        Each row has a list of two variables: one for the first 5 tiles
        and a second for the last 5 tiles.
        These variables are each a 5 digit number, where each digit is a value
        in `0..=4`.
        `0` represents a board tile that doesn't contain a unit.
        `1..=4` represent that a tile is filled and facing in the Direction
        associated with that number.
        """
        return self._board_tiles

    @staticmethod
    def col_variable(c: int) -> int:
        """
        Returns the "column index of board_tiles".

        If `c` is the index of a column stored in a row's first variable,
        returns `0`. Otherwise `c` is the index of a column stored in
        a row's second variable, and this method returns `1`.

        Parameters:
            c: The column index to process.
        Raises:
            ValueError: if `c < 0` or `c >= TETRIS_COLS
        """
        if c < 0 or TETRIS_COLS <= c:
            raise ValueError(f"{c} must be in {0}..{TETRIS_COLS}")
        return 0 if c < TETRIS_COLS // 2 else 1
