"""Container for the variables used in a scenario."""

from AoE2ScenarioParser.objects.triggers_obj import TriggerObject as TMgr
from AoE2ScenarioParser.objects.variable_obj import VariableObject as Var
from typing import List
from tetromino import Tetromino


class Variables:
    """An instance represents the variables used in a scenario."""

    def __init__(self, tmgr: TMgr):
        """
        Assigns variables to the scenario whose triggers are managed by `tmgr`.

        Parameters:
            tmgr: A scenario's trigger manager.
        """
        self._score = tmgr.add_variable('Score')
        self._selected = tmgr.add_variable('Selected Building')
        self._tseq = [tmgr.add_variable(f'Tetromino {k}')
                      for k in range(2 * Tetromino.num())]
        self._seq_index = tmgr.add_variable('Current Tetromino Index')
        self._facing = tmgr.add_variable('Facing')
        self._row = tmgr.add_variable('Row Index')
        self._col = tmgr.add_variable('Col Index')

    @property
    def score(self) -> Var:
        """
        Returns a variable for the player's Tetris score.

        The score is a nonnegative `int`.
        """
        return self._score

    @property
    def selected(self) -> Var:
        """
        Returns a variable for the player's select building.

        The variable's value represents the action corresponding to the
        selected building. The variable is set to 0 when no building
        is selected for the current game tick.
        """
        return self._selected

    @property
    def tseq(self) -> List[Var]:
        """
        Returns a list of variables for generating a sequence of Tetrominos.

        The length of the list is equal to twice the number of Tetrominos
        as specified by the Tetromino Enum.
        """
        return self._tseq

    @property
    def seq_index(self) -> Var:
        """
        Returns a variable containing the index in the Tetromino sequence.

        The Variable's value indicates the currently active Tetromino and
        must be in the range `0..Tetromino.num()`.
        """
        return self._seq_index

    @property
    def facing(self) -> Var:
        """
        Returns a variable to represent the active Tetromino's facing direction.

        The values of the variable correspond to the values of the
        Direction Enum.
        """
        return self._facing

    @property
    def row(self) -> Var:
        """
        Returns a variable containing the active Tetromino's row index.

        The variable's value is in `0..NUM_ROWS`.
        """
        # TODO get a specification for the number of rows.
        return self._row

    @property
    def col(self) -> Var:
        """
        Returns a variable containing the active Tetromino's col index.

        The variable's value is in `0..NUM_COLS`.
        """
        # TODO get a specification for the number of cols.
        return self._col
