"""Container for the variables used in a scenario."""

from AoE2ScenarioParser.objects.triggers_obj import TriggerObject as TMgr
from AoE2ScenarioParser.objects.variable_obj import VariableObject as Var

# The variable id of the player's score.
SCORE_ID = 0

# The variable id of the player's level.
LEVEL_ID = 1

# The variable id of the number of lines the player has cleared.
LINES_ID = 2


class ScnVar:
    """An instance represents a variable object and its initial value."""

    def __init__(self, tmgr: TMgr, name: str, init: int, var_id: int):
        """Initializes a new Variable with the given name and initial value."""
        self._var = tmgr.add_variable(name, var_id)
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
        self._score = ScnVar(tmgr, "Score", 0, SCORE_ID)
        self._level = ScnVar(tmgr, "Level", 0, LEVEL_ID)
        self._lines = ScnVar(tmgr, "Lines", 0, LINES_ID)

    @property
    def score(self) -> ScnVar:
        """
        Returns a variable for the player's Tetris score.

        The score is a nonnegative `int`.
        """
        return self._score

    @property
    def level(self) -> ScnVar:
        """
        Returns the player's level.

        The level starts at 1 and is incremented for every 10 lines cleared.
        """
        return self._level

    @property
    def lines(self) -> ScnVar:
        """Returns the number of cleared lines."""
        return self._lines
