"""Scenario objects collected for running a game of tetris."""


import math
from typing import Dict, Generator, List, Optional, Tuple
from AoE2ScenarioParser.datasets.buildings import Building, building_names
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.units import Unit
from AoE2ScenarioParser.objects.map_obj import MapObject as MMgr
from AoE2ScenarioParser.objects.unit_obj import UnitObject
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

# A `2 x 4` board of units.
DisplayBoard = List[List[UnitObject]]

# The outer list consists of 3 three lists, with the list at index `k`
# containing the render update triggers for the Tetromino at
# at `current_index + 1 + k`. That is, the first "next" piece's render triggers
# are at index `0`.
# Each inner list has index `c` as a trigger for rendering the Tetromino with
# value `c + 1`.
NextRenderTriggers = List[List[TriggerObject]]

# The element at index `k` is the hold render trigger for the `Tetromino` with
# `int` representation `k`. The element at index `0` is the hold render trigger
# for Invisible Objects.
HoldRenderTriggers = List[TriggerObject]

# The number of rows to leave between the start of rows of the next unit boards.
NEXT_ROW_SPACING = 4

# Unit constant for a Forage Bush, which is an "Other" object not yet
# added to the library.
FORAGE_BUSH = 59

# Unit constant for a map revealer, which isn't in any of the libraries.
# Replace if library is updated for "Other" units.
MAP_REVEALER = 837


PLACEHOLDER = Unit.INVISIBLE_OBJECT  # The unit used for board tiles.


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


def _rotate_unit_coordinates(
    mmgr: MMgr,
    rows: int,
    cols: int,
    space_v: float,
    space_h: float,
    r: int,
    c: int,
) -> Tuple[int, int]:
    """
    Returns the `(x, y)` coordinate on the map where the unit in row `r` and
    column `c` is positioned.
    """
    center_x = mmgr.map_width / 2.0 + 0.5
    center_y = mmgr.map_height / 2.0 + 0.5
    # Radians clockwise with 0 towards the northeast (along the x-axis).
    theta = 0.25 * math.pi
    start_x = center_x - 0.5 * space_h * (cols - 1)
    start_y = center_y - 0.75 * space_v * (rows - 1)
    # rotation by theta
    # [[cos(theta) -sin(theta)] [[x]  = [[x cos(theta) - y sin(theta)]
    #  [sin(theta) cos(theta)]]  [y]]    [x sin(theta) + y cos(theta)]]
    x0 = start_x + c * space_h - center_x
    y0 = start_y + r * space_v - center_y
    x = x0 * math.cos(theta) - y0 * math.sin(theta) + center_x
    y = x0 * math.sin(theta) + y0 * math.cos(theta) + center_y
    return (x, y)


def _generate_game_board(
    mmgr: MMgr,
    umgr: UMgr,
    rows: int,
    cols: int,
    visible: int,
    space_v: float,
    space_h: float,
) -> Board:
    """
    Places units in the middle of the map to use as the game board.

    Returns a 2D array of the units in the middle of the map.
    """
    board = Board(rows, cols, visible)
    for r in range(rows // 2, rows):
        for c in range(cols):
            x, y = _rotate_unit_coordinates(
                mmgr, rows, cols, space_v, space_h, r, c
            )
            for d in DIRECTIONS:
                assert board[Index(r, c)] is not None
                board[Index(r, c)][d] = umgr.add_unit(  # type: ignore
                    player=Player.ONE,
                    unit_const=PLACEHOLDER,
                    x=x,
                    y=y,
                    rotation=d.facing,
                )
    return board


def _generate_walls(
    mmgr: MMgr,
    umgr: UMgr,
    rows: int,
    cols: int,
    visible: int,
    space_v: float,
    space_h: float,
) -> Dict[Direction, List[Unit]]:
    """
    Returns the fortified wall objects used as targets for exploding rows.
    """

    def rotate(r: int, c: int) -> Tuple[float, float]:
        return _rotate_unit_coordinates(
            mmgr, rows, cols, space_v, space_h, r, c
        )

    walls = {}
    for d in (Direction.U, Direction.D):
        walls[d] = [None] * cols
        r = -20 if d == Direction.D else 80
        for c in range(cols):
            x, y = rotate(r, c)
            walls[d][c] = umgr.add_unit(
                player=Player.GAIA,
                unit_const=Building.FORTIFIED_WALL,
                x=x,
                y=y,
            )
    for d in (Direction.L, Direction.R):
        num_rows = rows - visible
        walls[d] = [None] * num_rows
        c = -40 if d == Direction.R else 50
        for r in range(visible, rows):
            x, y = rotate(r, c)
            walls[d][r - visible] = umgr.add_unit(
                player=Player.GAIA,
                unit_const=Building.FORTIFIED_WALL,
                x=x,
                y=y,
            )
    return walls


def _generate_next_units(
    mmgr: MMgr, umgr: UMgr, rows: int, cols: int, space_v: float, space_h: float
) -> List[DisplayBoard]:
    """Returns the boards used for displaying the next Tetrominos."""
    start_row = rows // 2 + 1
    next_boards = []
    for row in (
        start_row,
        start_row + NEXT_ROW_SPACING,
        start_row + 2 * NEXT_ROW_SPACING,
    ):
        board = []
        for r in (row, row + 1):
            board_row = []
            for c in range(cols + 3, cols + 7):
                x, y = _rotate_unit_coordinates(
                    mmgr, rows, cols, space_v, space_h, r, c
                )
                board_row.append(
                    umgr.add_unit(
                        player=Player.ONE,
                        unit_const=PLACEHOLDER,
                        x=x,
                        y=y,
                        rotation=Direction.U.facing,
                    )
                )
            board.append(board_row)
        next_boards.append(board)
    return next_boards


def _generate_hold_units(
    mmgr: MMgr, umgr: UMgr, rows: int, cols: int, space_v: float, space_h: float
) -> DisplayBoard:
    """Returns the board used for displaying the hold Tetromino"""
    start_row = rows // 2 + 1
    start_col = -7
    board = []
    for r in (start_row, start_row + 1):
        row = []
        for c in range(start_col, start_col + 4):
            x, y = _rotate_unit_coordinates(
                mmgr, rows, cols, space_v, space_h, r, c
            )
            row.append(
                umgr.add_unit(
                    player=Player.ONE,
                    unit_const=PLACEHOLDER,
                    x=x,
                    y=y,
                    rotation=Direction.U.facing,
                )
            )
        board.append(row)
    return board


def _declare_game_over_objective(tmgr: TMgr) -> TriggerObject:
    """Declares a trigger objective showing a message the game is over."""
    display_string = 'Game Over! Press "Select all Universities" to play again.'
    return tmgr.add_trigger(
        "Game Over Objective",
        display_as_objective=True,
        display_on_screen=True,
        description=display_string,
        short_description=display_string,
        mute_objectives=True,
        enabled=False,
        description_order=100,
    )


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
        description_order=0,
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


def _declare_render_next_triggers(tmgr: TMgr) -> NextRenderTriggers:
    """Returns the triggers for rendering the next Tetromino boards."""
    return [
        [
            tmgr.add_trigger(f"Render next {next_index} {t}", enabled=False)
            for t in list(Tetromino)
        ]
        for next_index in (0, 1, 2)
    ]


def _declare_render_hold_triggers(tmgr: TMgr) -> HoldRenderTriggers:
    """Returns the triggers for rendering the hold Tetromino board."""
    return [
        tmgr.add_trigger(f"Render hold {t}", enabled=False)
        for t in range(Tetromino.num() + 1)
    ]


def _declare_explode_row_triggers(
    tmgr: TMgr, rows: int, visible: int
) -> Dict[int, TriggerObject]:
    """Returns triggers for exploding rows with indices `visible:rows`."""
    return {
        r: tmgr.add_trigger(f"Explode Row {r}", enabled=False)
        for r in range(visible, rows)
    }


def _declare_clear_row_triggers(
    tmgr: TMgr, rows: int, visible: int
) -> Dict[int, TriggerObject]:
    """Returns triggers for exploding rows with indices `visible:rows`."""
    return {
        r: tmgr.add_trigger(f"Clear Row {r}", enabled=False)
        for r in range(visible, rows)
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
        space_v: float,
        space_h: float,
    ):
        """
        Initializes a `TetrisData` object writing to the input managers.

        `variables` are the variables used in the scenario, already added to
            the trigger manager.
        `building_x` is the x tile coordinate for spawning selection buildings.
        `building_y` is the y tile coordinate for spawning selection buildings.
        """
        self._visible = visible
        rev_len = mmgr.map_width // 2
        rev_offset = 15
        for x in range(rev_len - rev_offset, rev_len + rev_offset + 1):
            for y in range(rev_len - rev_offset, rev_len + rev_offset + 1):
                umgr.add_unit(
                    player=Player.ONE, unit_const=MAP_REVEALER, x=x, y=y
                )

        _place_invisible_objects(umgr)
        self._hotkeys = HotkeyBuildings(umgr, building_x, building_y)
        self._board = _generate_game_board(
            mmgr, umgr, rows, cols, visible, space_v, space_h
        )
        self._walls = _generate_walls(
            mmgr, umgr, rows, cols, visible, space_v, space_h
        )
        self._next_units = _generate_next_units(
            mmgr, umgr, rows, cols, space_v, space_h
        )
        self._hold_units = _generate_hold_units(
            mmgr, umgr, rows, cols, space_v, space_h
        )

        tmgr.add_trigger("-- Init --", enabled=False)
        self._init_scenario = tmgr.add_trigger("Init Scenario")

        tmgr.add_trigger("-- Objectives --", enabled=False)
        self._game_over_objective = _declare_game_over_objective(tmgr)
        self._new_game_objective = _declare_new_game_objective(tmgr)
        self._stat_obj = _declare_stat_objective(tmgr, variables)

        tmgr.add_trigger("-- Begin Game --", enabled=False)

        self._can_begin = tmgr.add_trigger("Can Begin Game")
        self._begin_game = tmgr.add_trigger("Begin Game", enabled=False)
        self._seq_init0 = _declare_sequence_init(tmgr, "Init a")
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
        self._shuffle = tmgr.add_trigger("Activate Shuffle", enabled=False)
        self._seq_init1 = _declare_sequence_init(tmgr, "Init b")

        tmgr.add_trigger("-- Rendering --")
        self._clear_rows = _declare_clear_row_triggers(tmgr, rows, visible)
        self._render_triggers = _declare_render_triggers(tmgr, rows, cols)
        self._render_next_triggers = _declare_render_next_triggers(tmgr)
        self._render_hold_triggers = _declare_render_hold_triggers(tmgr)
        self._explode_rows = _declare_explode_row_triggers(tmgr, rows, visible)
        self._react_tetris = tmgr.add_trigger("React Tetris", enabled=False)
        self._react_move = tmgr.add_trigger("React Move", enabled=False)
        self._react_hold = tmgr.add_trigger("React Hold", enabled=False)
        self._react_hold_fail = tmgr.add_trigger(
            "React Hold Fail", enabled=False
        )
        self._react_lock = tmgr.add_trigger("React Lock", enabled=False)
        self._game_over = tmgr.add_trigger("Game Over", enabled=False)
        self._react_game_over = tmgr.add_trigger(
            "React Game Over", enabled=False
        )
        self._react_game_over_easter = tmgr.add_trigger(
            "React Game Over Easter Egg", enabled=False
        )

        tmgr.add_trigger("-- Ending Game Loop --")
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
    def game_over_objective(self) -> TriggerObject:
        """Returns a trigger for an objective saying the game is over."""
        return self._game_over_objective

    @property
    def seq_init0(self) -> List[ProbTree]:
        """Returns the first sequence initialization triggers."""
        return self._seq_init0

    @property
    def can_begin(self) -> TriggerObject:
        """
        Returns a trigger for checking the condition of whether the first game
        can begin when the scenario initially is loaded or a new game can begin
        after a game of Tetris is over.
        """
        return self._can_begin

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
    def shuffle(self) -> TriggerObject:
        """Returns a trigger for shuffling the second Tetromino sequence."""
        return self._shuffle

    @property
    def seq_init1(self) -> List[ProbTree]:
        """Returns the second sequence initialization triggers."""
        return self._seq_init1

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
    def game_over(self) -> TriggerObject:
        """Returns a trigger for toggling the Game Over state."""
        return self._game_over

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

    @property
    def next_units(self) -> List[DisplayBoard]:
        """Returns a list of 3 render boards for showing the next Tetrominos."""
        return self._next_units

    @property
    def render_next_triggers(self) -> NextRenderTriggers:
        """Returns the triggers for rendering the next Tetromino boards."""
        return self._render_next_triggers

    @property
    def hold_units(self) -> DisplayBoard:
        """Returns the units for rendering the hold Tetromino."""
        return self._hold_units

    @property
    def render_hold_triggers(self) -> HoldRenderTriggers:
        """Returns the triggers for rendering the hold Tetromino board."""
        return self._render_hold_triggers

    @property
    def react_tetris(self) -> TriggerObject:
        """Returns a trigger to react to a player's clearing 4 lines."""
        return self._react_tetris

    @property
    def explode_rows(self) -> Dict[int, TriggerObject]:
        """
        Returns triggers for exploding rows with indices in `visible:rows`.
        """
        return self._explode_rows

    @property
    def clear_explodes(self) -> Dict[int, TriggerObject]:
        """
        Returns triggers for clearing exploding rows with indices in
        `visible:rows`.
        """
        return self._clear_rows

    @property
    def react_move(self) -> TriggerObject:
        """Returns a trigger to react to a Tetromino successfully moving."""
        return self._react_move

    @property
    def react_hold(self) -> TriggerObject:
        """Returns a trigger to react to a Tetromino being held."""
        return self._react_hold

    @property
    def react_hold_fail(self) -> TriggerObject:
        """Returns a trigger to react to a Tetromino failing to be held."""
        return self._react_hold_fail

    @property
    def react_lock(self) -> TriggerObject:
        """Returns a trigger to react to a Tetromino being locked."""
        return self._react_lock

    @property
    def react_game_over(self) -> TriggerObject:
        """Returns a trigger to react to the game being over."""
        return self._react_game_over

    @property
    def react_game_over_easter(self) -> TriggerObject:
        """
        Returns a trigger to react to the game being over with an Easter egg.
        """
        return self._react_game_over_easter

    def get_wall(self, r: int, c: int, d: Direction) -> UnitObject:
        """
        Returns the Fortified Wall unit that is targeted by an attacking unit
        on the tile at row `r` and column `c` when the attacker is facing in
        direction `d`.
        """
        return self._walls[d][
            c if d in {Direction.U, Direction.D} else r - self._visible
        ]

    def iter_walls(self) -> Generator[UnitObject, None, None]:
        """Iterates over the Fortified Wall targets."""
        for d in DIRECTIONS:
            yield from self._walls[d]
