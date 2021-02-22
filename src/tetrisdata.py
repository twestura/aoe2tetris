"""Scenario objects collected for running a game of tetris."""


import math
from typing import Dict, List
from AoE2ScenarioParser.datasets.buildings import Building, building_names
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.units import Unit
from AoE2ScenarioParser.objects.map_obj import MapObject as MMgr
from AoE2ScenarioParser.objects.unit_obj import UnitObject
from AoE2ScenarioParser.objects.units_obj import UnitsObject as UMgr
from AoE2ScenarioParser.objects.trigger_obj import TriggerObject
from AoE2ScenarioParser.objects.triggers_obj import TriggersObject as TMgr
from hotkeys import HotkeyBuildings, HOTKEY_BUILDINGS
from variables import ScnVar


# Game Board of units of dimension `TETRIS_ROWS` by `TETRIS_COLS`.
Board = List[List[UnitObject]]


def _place_invisible_objects(umgr: UMgr):
    """Places invisible objects in the left corner of the map."""
    for p in list(Player)[1:]:
        umgr.add_unit(
            player=p,
            unit_const=Unit.INVISIBLE_OBJECT,
            x=0,
            y=0,
        )


def _generate_game_board(mmgr: MMgr, umgr: UMgr,
                         rows: int, cols: int, space: float) -> Board:
    """
    Places units in the middle of the map to use as the game board.

    Returns a 2D array of the units in the middle of the map.
    """
    center_x = mmgr.map_width / 2.0 + 0.5
    center_y = mmgr.map_height / 2.0 + 0.5
    # Radians clockwise with 0 towards the northeast (along the x-axis).
    rotation = 0.75 * math.pi
    theta = 0.25 * math.pi

    start_x = center_x - 0.5 * ((cols - 1) * space)
    start_y = center_y - 0.5 * ((rows - 1) * space)

    # rotation by theta
    # [[cos(theta) -sin(theta)] [[x]  = [[x cos(theta) - y sin(theta)]
    #  [sin(theta) cos(theta)]]  [y]]    [x sin(theta) + y cos(theta)]]

    pieces = [[None] * cols for __ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            x0 = (start_x + c * space - center_x)
            y0 = (start_y + r * space - center_y)
            x = x0 * math.cos(theta) - y0 * math.sin(theta) + center_x
            y = x0 * math.sin(theta) + y0 * math.cos(theta) + center_y
            pieces[r][c] = umgr.add_unit(
                player=Player.ONE,
                unit_const=Unit.INVISIBLE_OBJECT,
                x=x,
                y=y,
                rotation=rotation
            )
    return pieces


def _declare_new_game_objective(tmgr: TMgr) -> TriggerObject:
    """Declares a trigger objective prompting to start a new game."""
    display_string = 'Press "Select all Universities" to begin a new game.'
    return tmgr.add_trigger(
        'New Game Instructions Objective',
        display_as_objective=True,
        display_on_screen=True,
        description=display_string,
        short_description=display_string
    )


def _declare_score_objective(tmgr: TMgr, score_var: ScnVar) -> TriggerObject:
    """Declares a trigger for the score objective."""
    display_string = f'Score: <{score_var.name}>'
    return tmgr.add_trigger(
        'Score Objective',
        display_as_objective=True,
        display_on_screen=True,
        description=display_string,
        short_description=display_string,
        enabled=False
    )


def _declare_selection_triggers(
        self,
        tmgr: TMgr) -> Dict[Building, TriggerObject]:
    """
    Declares the triggers for selecting buildings.

    Must be called near the start of the Game Loop to collect user input
    before the input is used in subsequent triggers.
    """
    return {
        b : tmgr.add_trigger(f'Select {building_names[b]}', enabled=False)
        for b in HOTKEY_BUILDINGS.keys()
    }


class TetrisData:
    """
    An instance represents the trigger declarations and units for Tetris.
    """
    def __init__(self, mmgr: MMgr, tmgr: TMgr, umgr: UMgr, score: ScnVar,
                 building_x: int, building_y: int,
                 rows: int, cols: int, space: float):
        """
        Initializes a `TetrisData` object writing to the input managers.

        `score` is the scenario variables representing a player's score.
        `building_x` is the x tile coordinate for spawning selection buildings.
        `building_y` is the y tile coordinate for spawning selection buildings.
        """
        _place_invisible_objects(umgr)
        self._hotkeys = HotkeyBuildings(umgr, building_x, building_y)
        self._board = _generate_game_board(mmgr, umgr, rows, cols, space)

        tmgr.add_trigger('-- Init --')
        self._init_scenario = tmgr.add_trigger('Init Scenario')

        tmgr.add_trigger('-- Objectives --')
        self._new_game_objective = _declare_new_game_objective(tmgr)
        self._score_obj = _declare_score_objective(tmgr, score)

        tmgr.add_trigger('-- Game Loop --')
        self._begin_game = tmgr.add_trigger('Begin Game')
        self._game_loop = tmgr.add_trigger(
            'Game Loop', enabled=False, looping=True
        )
        self._selection_triggers = _declare_selection_triggers(
            self._hotkeys, tmgr
        )
        self._move_left = tmgr.add_trigger('Move Left', enabled=False)
        self._move_right = tmgr.add_trigger('Move Right', enabled=False)
        self._cleanup = tmgr.add_trigger('Cleanup', enabled=False)

    @property
    def init_scenario(self) -> TriggerObject:
        """Returns a trigger for initializing scenario objects."""
        return self._init_scenario

    @property
    def new_game_objective(self) -> TriggerObject:
        """Returns a trigger for an objective to start a new game."""
        return self._new_game_objective

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
    def score_objective(self) -> TriggerObject:
        """Returns a trigger for displaying the player's score."""
        return self._score_obj

    @property
    def game_loop(self) -> TriggerObject:
        """Returns a trigger for starting the main game loop."""
        return self._game_loop

    @property
    def selection_triggers(self) -> Dict[Building, TriggerObject]:
        """Returns a mapping from a building id to its selection trigger."""
        return self._selection_triggers

    @property
    def cleanup(self) -> TriggerObject:
        """Returns a trigger for cleanup at the end of every game loop."""
        return self._cleanup
