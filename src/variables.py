"""Container for the variables used in a scenario."""

from AoE2ScenarioParser.objects.triggers_obj import TriggerObject as TMgr
from AoE2ScenarioParser.objects.variable_obj import VariableObject as Var
from typing import List
from direction import Direction
from tetromino import Tetromino


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


class Variables:
    """An instance represents the variables used in a scenario."""

    def __init__(self, tmgr: TMgr):
        """
        Assigns variables to the scenario whose triggers are managed by `tmgr`.

        Parameters:
            tmgr: A scenario's trigger manager.
        """
        self._score = ScnVar(tmgr, 'Score', 0)
        self._selected = ScnVar(tmgr, 'Selected Building', 0)
        tetrominos = list(Tetromino)
        self._tseq = [
            ScnVar(tmgr, f'Tetromino {k}', tetrominos[k % Tetromino.num()])
            for k in range(2 * Tetromino.num())
        ]
        self._seq_index = ScnVar(tmgr, 'Current Tetromino Index', 0)
        self._facing = ScnVar(tmgr, 'Facing', Direction.U.value)
        # TODO remove magic numbers
        self._row = ScnVar(tmgr, 'Row Index', 19)
        self._col = ScnVar(tmgr, 'Col Index', 4)

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
    def tseq(self) -> List[ScnVar]:
        """
        Returns a list of variables for generating a sequence of Tetrominos.

        The length of the list is equal to twice the number of Tetrominos
        as specified by the Tetromino Enum.
        """
        return self._tseq

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
        # TODO get a specification for the number of rows.
        return self._row

    @property
    def col(self) -> ScnVar:
        """
        Returns a variable containing the active Tetromino's col index.

        The variable's value is in `0..NUM_COLS`.
        """
        # TODO get a specification for the number of cols.
        return self._col
