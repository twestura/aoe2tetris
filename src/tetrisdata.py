"""Scenario objects collected for running a game of tetris."""


import math
from typing import Dict, List, Optional, Tuple
from AoE2ScenarioParser.datasets.buildings import Building, building_names
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.units import Unit
from AoE2ScenarioParser.objects.map_obj import MapObject as MMgr
from AoE2ScenarioParser.objects.units_obj import UnitsObject as UMgr
from AoE2ScenarioParser.objects.trigger_obj import TriggerObject
from AoE2ScenarioParser.objects.triggers_obj import TriggersObject as TMgr
from board import Board
from btreenode import BTreeNode
from direction import Direction
from hotkeys import HotkeyBuildings, HOTKEY_BUILDINGS
from index import Index
from probtree import ChanceNode, ProbTree
from tetromino import Tetromino
from variables import Variables

# Unit constant for a Forage Bush, which is an "Other" object not yet
# added to the library.
FORAGE_BUSH = 59

# Unit constant for a map revealer, which isn't in any of the libraries.
# Replace if library is updated for "Other" units.
MAP_REVEALER = 837


DIRECTIONS = list(Direction)  # List of all possible facing directions.
TETROMINOS = list(Tetromino)  # List of all Tetris pieces.


def _place_invisible_objects(umgr: UMgr):
    """Places invisible objects in the left corner of the map."""
    for p in list(Player)[1:]:
        umgr.add_unit(
            player=p,
            unit_const=Unit.INVISIBLE_OBJECT,
            x=0,
            y=0,
        )


def _generate_game_board(
    mmgr: MMgr, umgr: UMgr, rows: int, cols: int, visible: int, space: float
) -> Board:
    """
    Places units in the middle of the map to use as the game board.

    Returns a 2D array of the units in the middle of the map.
    """
    center_x = mmgr.map_width / 2.0 + 0.5
    center_y = mmgr.map_height / 2.0 + 0.5
    # Radians clockwise with 0 towards the northeast (along the x-axis).
    theta = 0.25 * math.pi

    start_x = center_x - 0.5 * space * (cols - 1)
    start_y = center_y - 0.75 * space * (rows - 1)

    # rotation by theta
    # [[cos(theta) -sin(theta)] [[x]  = [[x cos(theta) - y sin(theta)]
    #  [sin(theta) cos(theta)]]  [y]]    [x sin(theta) + y cos(theta)]]

    board = Board(rows, cols, visible)
    for r in range(rows // 2, rows):
        for c in range(cols):
            x0 = start_x + c * space - center_x
            y0 = start_y + r * space - center_y
            x = x0 * math.cos(theta) - y0 * math.sin(theta) + center_x
            y = x0 * math.sin(theta) + y0 * math.cos(theta) + center_y
            for d in DIRECTIONS:
                assert board[Index(r, c)] is not None
                board[Index(r, c)][d] = umgr.add_unit(  # type: ignore
                    player=Player.ONE,
                    unit_const=Unit.INVISIBLE_OBJECT,
                    x=x,
                    y=y,
                    rotation=d.facing,
                )
    return board


def _declare_new_game_objective(tmgr: TMgr) -> TriggerObject:
    """Declares a trigger objective prompting to start a new game."""
    display_string = 'Press "Select all Universities" to begin a new game.'
    return tmgr.add_trigger(
        "New Game Instructions Objective",
        display_as_objective=True,
        display_on_screen=True,
        description=display_string,
        short_description=display_string,
        mute_objectives=True,
    )


def _declare_stat_objective(tmgr: TMgr, variables: Variables) -> TriggerObject:
    """Declares an objective trigger for displaying score, level, and lines."""
    display_string = "\n".join(
        [
            f"Score: <{variables.score.name}>",
            f"Level: <{variables.level.name}>",
            f"Lines: <{variables.lines.name}>",
        ]
    )
    return tmgr.add_trigger(
        "Stats Objective",
        display_as_objective=True,
        display_on_screen=True,
        description=display_string,
        short_description=display_string,
        mute_objectives=True,
        enabled=False,
    )


def _declare_prob_tree(tmgr: TMgr, n: int, pre: str = None) -> ProbTree:
    """
    Adds triggers for generating a random number between 0 and n inclusive.

    `pre` is a prefix to prepend to the trigger names.
    Raises a `ValueError` if `n` is nonpositive.
    """
    # Note there are still some unnecessary triggers for swapping index 0.
    if n < 1:
        raise ValueError(f"{n} must be positive.")
    name_prefix = f"{pre} Generate 0--{n}" if pre else f"Generate 0--{n}"
    name_char = "a"

    def declare_range(left: int, right: int) -> ProbTree:
        """Returns a `ProbTree` for generating numbers in `left:right`."""
        nonlocal name_char
        total = right - left
        assert total > 1
        mid = left + (right - left) // 2
        num_left = mid - left
        num_right = right - mid
        percent = int(100.0 * round(num_left / total, 2))
        success = tmgr.add_trigger(
            f"{name_prefix} {name_char} success", enabled=False
        )
        name_char = chr(ord(name_char) + 1)
        failure = tmgr.add_trigger(
            f"{name_prefix} {name_char} failure", enabled=False
        )
        name_char = chr(ord(name_char) + 1)
        return BTreeNode(
            ChanceNode(percent, success, failure),
            BTreeNode(left) if num_left == 1 else declare_range(left, mid),
            BTreeNode(right - 1)
            if num_right == 1
            else declare_range(mid, right),
        )

    return declare_range(0, n + 1)


def _declare_rand_int_triggers(tmgr: TMgr, pre: str = None) -> List[ProbTree]:
    """
    Returns a list of Trees for generating random numbers.

    That is, returns `[t6, t5, t4, t3, t2, t1]`, where tn is the tree used for
    generating a random number from `0` through `n`, inclusive.
    `pre` is a prefix to prepend to the trigger names.
    """
    return [
        _declare_prob_tree(tmgr, n, pre)
        for n in range(Tetromino.num() - 1, 0, -1)
    ]


def _declare_sequence_init(tmgr: TMgr, pre: str) -> List[ProbTree]:
    """
    Returns a list for the probability tree triggers needed to initialize
    the Tetromino sequences at the start of the game.

    `pre` is a prefix to prepend to the trigger names.
    """
    return _declare_rand_int_triggers(tmgr, pre)


def _declare_selection_triggers(tmgr: TMgr) -> Dict[Building, TriggerObject]:
    """
    Declares the triggers for selecting buildings.

    Must be called near the start of the Game Loop to collect user input
    before the input is used in subsequent triggers.
    """
    return {
        b: tmgr.add_trigger(f"Select {building_names[b]}", enabled=False)
        for b in HOTKEY_BUILDINGS.keys()
    }


def _declare_render_triggers(
    tmgr: TMgr, rows: int, cols: int
) -> Dict[Tuple[Index, Direction, Optional[Tetromino]], TriggerObject]:
    """
    Returns a dictionary mapping state information to a render trigger.

    The state information is a row, column, facing direction, and
    tetromino. This state indicates the unit to be placed for the game
    board.

    The trigger replaces the unit if it updated during the current
    game ticks update stage.
    """
    return {
        (Index(r, c), d, None if t == 0 else Tetromino(t),): tmgr.add_trigger(
            f"Render ({r}, {c}), {str(d)}, {str(t)}", enabled=False
        )
        # for r in range(rows // 2, rows // 2 + 1)  # Tests one row
        # for r in range(rows // 2, rows // 2 + 3)  # Tests 3 rows
        for r in range(rows // 2, rows)
        # for c in range(cols // 2 - 1, cols // 2)  # Tests 1 column
        for c in range(cols)
        # for d in [Direction.U]  # Tests 1 direction
        for d in list(Direction)
        for t in range(Tetromino.num() + 1)
    }


class TetrisData:
    """
    An instance represents the trigger declarations and units for Tetris.
    """

    def __init__(
        self,
        mmgr: MMgr,
        tmgr: TMgr,
        umgr: UMgr,
        variables: Variables,
        building_x: int,
        building_y: int,
        rows: int,
        cols: int,
        visible: int,
        space: float,
    ):
        """
        Initializes a `TetrisData` object writing to the input managers.

        `variables` are the variables used in the scenario, already added to
            the trigger manager.
        `building_x` is the x tile coordinate for spawning selection buildings.
        `building_y` is the y tile coordinate for spawning selection buildings.
        """

        # TODO remove test map revealers
        revealer_len = mmgr.map_width // 2
        revlenadj = 15
        for x in range(revealer_len - revlenadj, revealer_len + revlenadj):
            for y in range(revealer_len - revlenadj, revealer_len + revlenadj):
                umgr.add_unit(
                    player=Player.ONE, unit_const=MAP_REVEALER, x=x, y=y
                )

        _place_invisible_objects(umgr)
        self._hotkeys = HotkeyBuildings(umgr, building_x, building_y)
        self._board = _generate_game_board(
            mmgr, umgr, rows, cols, visible, space
        )

        tmgr.add_trigger("-- Init --", enabled=False)
        self._init_scenario = tmgr.add_trigger("Init Scenario")

        tmgr.add_trigger("-- Objectives --", enabled=False)
        self._new_game_objective = _declare_new_game_objective(tmgr)
        self._stat_obj = _declare_stat_objective(tmgr, variables)

        tmgr.add_trigger("-- Begin Game --", enabled=False)

        self._can_begin_initial = tmgr.add_trigger("Can Begin First Game")
        self._begin_game = tmgr.add_trigger("Begin Game", enabled=False)
        self._seq_init0 = _declare_sequence_init(tmgr, "Init a")
        self._seq_init1 = _declare_sequence_init(tmgr, "Init b")
        self._begin_game_mid = tmgr.add_trigger(
            "Begin Game Middle", enabled=False
        )

        tmgr.add_trigger("-- Game Loop --")
        self._game_loop = tmgr.add_trigger(
            "Game Loop", enabled=False, looping=True
        )
        self._selection_triggers = _declare_selection_triggers(tmgr)
        self._new_game = tmgr.add_trigger("New Game", enabled=False)
        self._update = tmgr.add_trigger("Update", enabled=False)
        self._render_triggers = _declare_render_triggers(tmgr, rows, cols)
        self._cleanup = tmgr.add_trigger("Cleanup", enabled=False)
        self._begin_game_end = tmgr.add_trigger("Begin Game End", enabled=False)

    @property
    def init_scenario(self) -> TriggerObject:
        """Returns a trigger for initializing scenario objects."""
        return self._init_scenario

    @property
    def new_game_objective(self) -> TriggerObject:
        """Returns a trigger for an objective to start a new game."""
        return self._new_game_objective

    @property
    def seq_init0(self) -> List[ProbTree]:
        """Returns the first sequence initialization triggers."""
        return self._seq_init0

    @property
    def seq_init1(self) -> List[ProbTree]:
        """Returns the second sequence initialization triggers."""
        return self._seq_init1

    # @property
    # def place_init_piece(self) -> Dict[Tetromino, TriggerObject]:
    #     """
    #     Returns the triggers for placing a Tetromino at the start.

    #     Maps a Tetromino to the trigger for placing it.
    #     """
    # return self._place_init_piece

    @property
    def can_begin_initial(self) -> TriggerObject:
        """
        Returns a trigger for checking the condition of whether the first game
        can begin when the scenario initially is loaded.
        """
        return self._can_begin_initial

    @property
    def begin_game(self) -> TriggerObject:
        """Returns a trigger for beginning the game of Tetris."""
        return self._begin_game

    @property
    def hotkeys(self) -> HotkeyBuildings:
        """Returns the manager for buildings and selection hotkeys."""
        return self._hotkeys

    @property
    def board(self) -> Board:
        """Returns a `TETRIS_ROWS` by `TETRIS_COLS` 2d-list of board pieces."""
        return self._board

    @property
    def stat_objective(self) -> TriggerObject:
        """Returns a trigger for displaying the player's score."""
        return self._stat_obj

    @property
    def begin_game_mid(self) -> TriggerObject:
        """Returns a trigger for updating the render data after shuffling."""
        return self._begin_game_mid

    @property
    def game_loop(self) -> TriggerObject:
        """Returns a trigger for starting the main game loop."""
        return self._game_loop

    @property
    def selection_triggers(self) -> Dict[Building, TriggerObject]:
        """Returns a mapping from a building id to its selection trigger."""
        return self._selection_triggers

    @property
    def new_game(self) -> TriggerObject:
        """Returns a trigger for starting a new game."""
        return self._new_game

    @property
    def update(self) -> TriggerObject:
        """Returns a trigger for acting on user input and updating state."""
        return self._update

    @property
    def render_triggers(
        self,
    ) -> Dict[Tuple[Index, Direction, Optional[Tetromino]], TriggerObject]:
        """
        Returns a dictionary mapping state information to a render trigger.

        The state information is a row, column, facing direction, and
        tetromino. This state indicates the unit to be placed for the game
        board.

        The trigger replaces the unit if it updated during the current
        game ticks update stage.
        """
        return self._render_triggers

    @property
    def cleanup(self) -> TriggerObject:
        """Returns a trigger for cleanup at the end of every game loop."""
        return self._cleanup

    @property
    def begin_game_end(self) -> TriggerObject:
        """
        Returns a trigger for ending the begin game phase and starting the
        game loop.
        """
        return self._begin_game_end
