"""
Command line application to build the scenario files for Aoe2 Tetris.

Uses the scenario file parsing library found here:
https://github.com/ksneijders/aoe2scenarioparser
"""


from __future__ import annotations
from AoE2ScenarioParser.aoe2_scenario import AoE2Scenario
from AoE2ScenarioParser.datasets.buildings import Building, building_names
from AoE2ScenarioParser.datasets.conditions import Condition
from AoE2ScenarioParser.datasets.effects import Effect
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.trigger_lists import Comparison, ObjectAttribute, Operation
from AoE2ScenarioParser.datasets.units import Unit
from AoE2ScenarioParser.objects.map_obj import MapObject as MMgr
from AoE2ScenarioParser.objects.unit_obj import UnitObject
from AoE2ScenarioParser.objects.units_obj import UnitsObject as UMgr
from AoE2ScenarioParser.objects.trigger_obj import TriggerObject
from AoE2ScenarioParser.objects.triggers_obj import TriggersObject as TMgr
from AoE2ScenarioParser.objects.variable_obj import VariableObject as Var
from action import Action
from enum import Enum
from btreenode import BTreeNode
from probtree import ChanceNode, ProbTree
from typing import Any, Dict, List, Tuple, Union
from variables import Variables
import argparse
import math
import os.path
import random

# Trigger headers for testing Fisher Yates.
# The first element is a trigger for running a test loop.
# The second element is a `NUM_TETROMINO` by `NUM_TETROMINO` list indexed
# by debug slot and then player color.
# TODO add the Fisher Yates randomization triggers along with the loop and
# the create object triggers.
Test_FY_Triggers = Tuple[TriggerObject, List[List[TriggerObject]]]


SCN_EXT = 'aoe2scenario' # Scenario file extension.
OUT_SCN_DIR = 'out-scns' # Output directory for built files.
OUT_FILENAME = 'Tetris' # Name of the main scenario.

PLAYERS = list(Player) # List of all player constants.

TETRIS_ROWS = 20 # The number of rows in a game of tetris.
TETRIS_COLS = 10 # The number of columns in a game of tetris.

# Game Board of units of dimension `TETRIS_ROWS` by `TETRIS_COLS`.
Board = List[List[UnitObject]]

SQUARE_SPACE = 1.0 # The amount of space between Tetris game squares.

BUILDING_X = 2 # The x-coordinate to place "select all hotkey" buildings.
BUILDING_Y = 2 # The y-coordinate to place "select all hotkey" buildings.

NUM_TETROMINO = 7 # The number of different Tetris pieces.

# Maps a player slot to the string name of that player's color.
PLAYER_COLOR_NAMES = {
    Player.TWO : 'Red',
    Player.THREE : 'Green',
    Player.FOUR : 'Yellow',
    Player.FIVE : 'Cyan',
    Player.SIX : 'Purple',
    Player.SEVEN : 'Blue',
    Player.EIGHT : 'Orange'
}

# Maps a player number to the associated Tetromino unit id.
PLAYER_TETROMINO = {
    Player.TWO : Unit.ELITE_BERSERK,
    Player.THREE : Unit.ELITE_HUSKARL,
    Player.FOUR : Unit.ELITE_THROWING_AXEMAN,
    Player.FIVE : Unit.ELITE_TEUTONIC_KNIGHT,
    Player.SIX : Unit.ELITE_SAMURAI,
    Player.SEVEN : Unit.ELITE_WOAD_RAIDER,
    Player.EIGHT : Unit.ELITE_LONGBOWMAN
}

FY_TEST_SLOT_X = 10 # The first x coordinate for placing test pieces.
FY_TEST_SLOT_Y = 0 # The y coordinate for all test pieces.


_SWAP_MESSAGE_GLOBAL = 0 # Hack to make each swap function have its own name.


# Maps the building id of a select all building hotkey to the actions that
# selecting the building performs.
HOTKEY_BUILDINGS = {
    Building.ARCHERY_RANGE : Action.MOVE_LEFT,
    # TODO switch Barracks for Blacksmith
    Building.BARRACKS : Action.MOVE_RIGHT,
    Building.STABLE : Action.ROTATE_CLOCKWISE,
    Building.MARKET : Action.ROTATE_COUNTERCLOCKWISE,
    Building.MONASTERY : Action.SOFT_DROP,
    Building.CASTLE : Action.HARD_DROP,
    Building.SIEGE_WORKSHOP : Action.HOLD
}


class HotkeyBuildings:
    """A container for the buildings, triggers, and variables for hotkeys."""

    def __init__(self, tmgr: TMgr, umgr: UMgr):
        """
        Places units on the map and declares triggers and variabels.

        Units are initially placed as Invisible Objects,
        then modified to have 0 Line of Sight,
        then changed to their respective buildings.
        """
        self._selected_var = tmgr.add_variable('Selected Building')
        self._init = tmgr.add_trigger('Initialize Buildings')
        self._building_map = {
            bid : umgr.add_unit(
                player=Player.GAIA,
                unit_const=bid,
                x = BUILDING_X,
                y = BUILDING_Y
            )
            for bid in HOTKEY_BUILDINGS.keys()
        }
        # TODO refactor this declaration because of dependency
        self._selection_triggers = None

    @property
    def selected_var(self) -> VariableObject:
        """Returns a variable for determining which object is selected."""
        return self._selected_var

    @property
    def init_buildings(self) -> TriggerObject:
        """
        Returns a trigger for initializing the buildings.

        The trigger modifies their line of sight to be `0` and replaces the
        Invisible Objects with their respective buildings.
        """
        return self._init

    @property
    def building_map(self) -> Dict[Building, UnitObject]:
        """Returns a mapping from a building id to the unit paced on the map."""
        return self._building_map

    @property
    def selection_triggers(self) -> List[List[TriggerObject]]:
        """
        Returns a 2d list of the triggers for determining user input.

        Each element of the list is a 2d list of buildings where
        the ownership is swapped whenever one is selected.
        """
        return self._selection_triggers

    def declare_selection_triggers(
            self,
            tmgr: TMgr) -> Dict[Building, TriggerObject]:
        """
        Declares the triggers for selecting buildings.

        Must be called near the start of the Game Loop to collect user input
        before the input is used in subsequent triggers.
        """
        self._selection_triggers = {
            b : tmgr.add_trigger(f'Select {building_names[b]}', enabled=False)
            for b in HOTKEY_BUILDINGS.keys()
        }


def output_path() -> str:
    """Returns the output path for the generated scenario file."""
    return os.path.join(OUT_SCN_DIR, f'{OUT_FILENAME}.{SCN_EXT}')


def _swap_msg(id0: int, id1: int) -> str:
    """Returns a string message for a `swap(id0, id1)` script call."""
    global _SWAP_MESSAGE_GLOBAL
    _SWAP_MESSAGE_GLOBAL += 1
    return '\n'.join([
        f'void _{_SWAP_MESSAGE_GLOBAL}() ' + '{',
        f'    swap({id0}, {id1});',
        '}'
    ])


def _place_invisible_objects(umgr: UMgr):
    """Places invisible objects in the left corner of the map."""
    for p in PLAYERS[1:]:
        umgr.add_unit(
            player=p,
            unit_const=Unit.INVISIBLE_OBJECT,
            x=0,
            y=0,
        )


def _generate_game_board(mmgr: MMgr, umgr: UMgr) -> Board:
    """
    Places units in the middle of the map to use as the game board.

    Returns a 2D array of the units in the middle of the map.
    """
    center_x = mmgr.map_width / 2.0 + 0.5
    center_y = mmgr.map_height / 2.0 + 0.5
    # Radians clockwise with 0 towards the northeast (along the x-axis).
    rotation = 0.75 * math.pi
    theta = 0.25 * math.pi

    start_x = center_x - 0.5 * ((TETRIS_COLS - 1) * SQUARE_SPACE)
    start_y = center_y - 0.5 * ((TETRIS_ROWS - 1) * SQUARE_SPACE)

    # rotation by theta
    # [[cos(theta) -sin(theta)] [[x]  = [[x cos(theta) - y sin(theta)]
    #  [sin(theta) cos(theta)]]  [y]]    [x sin(theta) + y cos(theta)]]

    pieces = [[None] * TETRIS_COLS for __ in range(TETRIS_ROWS)]
    for r in range(TETRIS_ROWS):
        for c in range(TETRIS_COLS):
            x0 = (start_x + c * SQUARE_SPACE - center_x)
            y0 = (start_y + r * SQUARE_SPACE - center_y)
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


def _declare_variables(tmgr: TMgr) -> List[List[VariableObject]]:
    """
    Declares the variables used by triggers in the scenario.

    Returns a 2x7 2d-list of the variables.
    Row 1 consists of the "current" tetris piece variables.
    Row 2 consists of the "next" pieces after the first row is exhausted.
    """
    current_pieces = [tmgr.add_variable(f'Tetromino {k}')
                      for k in range(NUM_TETROMINO)]
    next_pieces = [tmgr.add_variable(f'Tetromino {k}')
                   for k in range(NUM_TETROMINO, 2*NUM_TETROMINO)]
    return [current_pieces, next_pieces]


def _add_test_init_var_trigger(tmgr: TMgr) -> TriggerObject:
    """TODO testing function that should be replaced."""
    # TODO display objective as variable debugger
    return tmgr.add_trigger('Initialize Tetromino Variables TEST')


def _add_score_variable(tmgr: TMgr) -> VariableObject:
    """Adds and returns a variable for the player's score."""
    return tmgr.add_variable('score')


def _init_score(tmgr: TMgr) -> TriggerObject:
    """Returns a trigger declaration for initializing the player's score."""
    return tmgr.add_trigger('Initialize Score')


def _declare_score_obj(tmgr: TMgr, score_var: VariableObject) -> TriggerObject:
    """Declares a trigger for the score objective."""
    display_string = f'Score: <{score_var.name}>'
    return tmgr.add_trigger(
        'Score Objective',
        display_as_objective=True,
        display_on_screen=True,
        description=display_string,
        short_description=display_string
    )


def _declare_prob_tree(tmgr: TMgr, n: int) -> ProbTree:
    """
    Adds triggers for generating a random number between 0 and n inclusive.

    Raises a `ValueError` if `n` is nonpositive.
    """
    # TODO there are still some unnecessary triggers for swapping index 0.
    if n < 1:
        raise ValueError(f'{n} must be positive.')
    name_prefix = f'Generate 0--{n}'
    name_char = 'a'

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
            f'{name_prefix} {name_char} success',
            enabled=False
        )
        name_char = chr(ord(name_char) + 1)
        failure = tmgr.add_trigger(
            f'{name_prefix} {name_char} failure',
            enabled=False
        )
        name_char = chr(ord(name_char) + 1)
        return BTreeNode(
            ChanceNode(percent, success, failure),
            BTreeNode(left) if num_left == 1 else declare_range(left, mid),
            BTreeNode(right - 1) if num_right == 1 else declare_range(mid, right)
        )
    return declare_range(0, n + 1)


def _declare_activate_random(tmgr: TMgr) -> TriggerObject:
    """Returns a trigger declaration for activating random number generation."""
    return tmgr.add_trigger('Fisher Yates Permutation', enabled=False)


def _declare_rand_int_triggers(tmgr: TMgr) -> List[ProbTree]:
    """
    Returns a list of Trees for generating random numbers.

    That is, returns `[t6, t5, t4, t3, t2, t1]`, where tn is the tree used for
    generating a random number from `0` through `n`, inclusive.
    """
    return [_declare_prob_tree(tmgr, n) for n in range(NUM_TETROMINO-1, 0, -1)]


def _declare_test_piece_triggers(tmgr: TMgr) -> Test_FY_Triggers:
    """TODO specify, testing function."""
    main_loop = tmgr.add_trigger('Randomize And Place Test Row', looping=True)
    triggers = [[None] * NUM_TETROMINO for __ in range(NUM_TETROMINO)]
    for k in range(NUM_TETROMINO):
        for (p, player) in enumerate(PLAYERS[2:]):
            color = PLAYER_COLOR_NAMES[player]
            triggers[k][p] = tmgr.add_trigger(
                f'Place {color} in slot {k}',
                enabled=False
            )
    return (main_loop, triggers)


class TetrisData:
    """
    The objects created while generating a game of Tetris.
    """
    def __init__(self, mmgr: MMgr, tmgr: TMgr, umgr: UMgr):
        """Creates and initializes a TetrisData object."""

        # TODO remove test cataphract
        center_x = mmgr.map_width / 2.0 + 0.5
        center_y = mmgr.map_height / 2.0 + 0.5
        rotation = 0.75 * math.pi
        self._test_cata = umgr.add_unit(
            player=Player.ONE,
            unit_const=Unit.ELITE_CATAPHRACT,
            x=center_x,
            y=center_y,
            rotation=rotation
        )

        tmgr.add_trigger('-- Init --')
        _place_invisible_objects(umgr)
        self._hotkeys = HotkeyBuildings(tmgr, umgr)
        self._board = _generate_game_board(mmgr, umgr)
        self._piece_vars = _declare_variables(tmgr)
        self._score_var = _add_score_variable(tmgr)
        self._test_init_var_trigger = _add_test_init_var_trigger(tmgr)
        self._init_score = _init_score(tmgr)

        tmgr.add_trigger('-- Objectives --')
        self._score_obj = _declare_score_obj(tmgr, self._score_var)

        tmgr.add_trigger('-- Game Loop --')
        self._game_loop = tmgr.add_trigger('Game Loop', looping=True)
        self._hotkeys.declare_selection_triggers(tmgr)
        self._move_left = tmgr.add_trigger('Move Left', enabled=False)
        self._move_right = tmgr.add_trigger('Move Right', enabled=False)
        # self._activate_random = _declare_activate_random(tmgr)
        # self._rand_int_trees = _declare_rand_int_triggers(tmgr)
        # self._test_piece_triggers = _declare_test_piece_triggers(tmgr)
        self._cleanup = tmgr.add_trigger('Cleanup', enabled=False)

    @property
    def hotkeys(self) -> HotkeyBuildings:
        """Returns the manager for buildings and selection hotkeys."""
        return self._hotkeys

    @property
    def board(self) -> Board:
        """Returns a `TETRIS_ROWS` by `TETRIS_COLS` 2d-list of board pieces."""
        return self._board

    @property
    def piece_vars(self) -> List[List[VariableObject]]:
        """Returns a 2x7 list of "current" and "next" Tetromino variables."""
        return self._piece_vars

    @property
    def score_var(self) -> VariableObject:
        """Returns a variable for keeping track of the player's Tetris score."""
        return self._score_var

    @property
    def score_initializer(self) -> TriggerObject:
        """Returns a trigger for setting the player's starting score."""
        return self._init_score

    @property
    def score_objective(self) -> TriggerObject:
        """Returns a trigger for displaying the player's score."""
        return self._score_obj

    @property
    def game_loop(self) -> TriggerObject:
        """Returns a trigger for starting the main game loop."""
        return self._game_loop

    # @property
    # def activate_random(self) -> TriggerObject:
    #     """Returns a trigger for performing the Fisher Yates permutation."""
    #     return self._activate_random

    # @property
    # def rand_int_trees(self) -> List[PropTree]:
    #     """
    #     Returns a list of random integer trigger trees.

    #     The returned list is `[t6, t5, t4, t3, t2, t1]`, where `tn` is a tree
    #     for generating numbers from `0` to `n`, inclusive.
    #     """
    #     return self._rand_int_trees

    @property
    def cleanup(self) -> TriggerObject:
        """Returns a trigger for cleanup at the end of every game loop."""
        return self._cleanup


def _impl_move_left_right(tdata: TetrisData):
    """Implements moving the test Cataphract left and right."""
    cata = tdata._test_cata
    tdata._move_left.add_condition(
        Condition.VARIABLE_VALUE,
        amount_or_quantity=Action.MOVE_LEFT.value,
        variable=tdata.hotkeys.selected_var.variable_id,
        comparison=Comparison.EQUAL
    )
    tdata._move_left.add_effect(
        Effect.TELEPORT_OBJECT,
        selected_object_ids=cata.reference_id,
        location_x=71,
        location_y=71,
    )
    tdata._move_right.add_condition(
        Condition.VARIABLE_VALUE,
        amount_or_quantity=Action.MOVE_RIGHT.value,
        variable=tdata.hotkeys.selected_var.variable_id,
        comparison=Comparison.EQUAL
    )
    tdata._move_right.add_effect(
        Effect.TELEPORT_OBJECT,
        selected_object_ids=cata.reference_id,
        location_x=73,
        location_y=73,
    )


def _impl_game_loop(tdata: TetrisData):
    """Implements the main game loop trigger."""
    tdata.game_loop.add_effect(
        Effect.CHANGE_VARIABLE,
        quantity=0,
        operation=Operation.SET,
        from_variable=tdata.hotkeys.selected_var.variable_id
    )

    selection_triggers = list(tdata.hotkeys.selection_triggers.values())
    for t in selection_triggers:
        tdata.game_loop.add_effect(
            Effect.ACTIVATE_TRIGGER,
            trigger_id=t.trigger_id
        )
    for t in [tdata._move_left, tdata._move_right]:
        tdata.game_loop.add_effect(
            Effect.ACTIVATE_TRIGGER,
            trigger_id=t.trigger_id
        )
        # TODO create local "selection trigger" cleanup trigger
        tdata.cleanup.add_effect(
            Effect.DEACTIVATE_TRIGGER,
            trigger_id=t.trigger_id
        )

    # Building Selected
    for b, t in tdata.hotkeys.selection_triggers.items():
        bid = tdata.hotkeys.building_map[b].reference_id
        t.add_condition(
            Condition.OBJECT_SELECTED,
            unit_object=bid
        )
        t.add_effect(
            Effect.CHANGE_VARIABLE,
            quantity=HOTKEY_BUILDINGS[b].value,
            operation=Operation.SET,
            from_variable=tdata.hotkeys.selected_var.variable_id
        )
        for src, tar in [(Player.ONE, Player.GAIA), (Player.GAIA, Player.ONE)]:
            t.add_effect(
                Effect.CHANGE_OWNERSHIP,
                source_player=src,
                target_player=tar,
                selected_object_ids=bid
            )
    for i in range(len(selection_triggers) - 1):
        for j in range(i+1, len(selection_triggers)):
            selection_triggers[i].add_effect(
                Effect.DEACTIVATE_TRIGGER,
                trigger_id=selection_triggers[j].trigger_id
            )

    _impl_move_left_right(tdata)

    tdata._game_loop.add_effect(
        Effect.ACTIVATE_TRIGGER,
        trigger_id=tdata.cleanup.trigger_id
    )


def _impl_hotkeys(tdata: TetrisData):
    """Implements the building selection hotkeys and variables."""
    for b in HOTKEY_BUILDINGS.keys():
        for p in (Player.GAIA, Player.ONE):
            tdata.hotkeys.init_buildings.add_effect(
                Effect.MODIFY_ATTRIBUTE,
                quantity=0,
                object_list_unit_id=b,
                source_player=p,
                operation=Operation.SET,
                object_attributes=ObjectAttribute.LINE_OF_SIGHT
            )
    tdata.hotkeys.init_buildings.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.GAIA,
        target_player=Player.ONE,
        selected_object_ids=[
            b.reference_id for b in tdata.hotkeys.building_map.values()
        ]
    )


def _impl_piece_vars(tdata: TetrisData, tmgr: TMgr):
    """Implements the triggers for placing the tetromino variables."""
    for pieces in tdata.piece_vars:
        for k, var in enumerate(pieces):
            tdata._test_init_var_trigger.add_effect(
                Effect.CHANGE_VARIABLE,
                quantity=k+2,
                operation=Operation.SET,
                from_variable=var.variable_id
            )


def _impl_objectives(tdata: TetrisData, tmgr: TMgr):
    """Implements the triggers to initialize and display player score."""
    tdata.score_initializer.add_effect(
        Effect.CHANGE_VARIABLE,
        quantity=0,
        operation=Operation.SET,
        from_variable=tdata.score_var.variable_id
    )
    tdata.score_objective.add_condition(
        Condition.PLAYER_DEFEATED,
        source_player=Player.GAIA
    )

def _impl_rand_tree(tdata: TetrisData, tmgr: TMgr, tree: ProbTree):
    """
    Implements the triggers for `tree`.

    Requires that `tree` stores `ChanceNode` data (not `int` data).
    Requires that the root `tree` node's `success` and `failure` triggers
        are activated by a trigger that occurs in `tmgr`'s trigger list
        before any of the `success` or `failure` triggers in the tree.
    """
    current_pieces = tdata.piece_vars[0]
    var_id0 = current_pieces[0].variable_id
    nodes = [tree] # The internal tree nodes with triggers to implement.
    while nodes:
        n = nodes.pop()
        assert not isinstance(n.data, int)
        percent = n.data.percent
        success = n.data.success
        failure = n.data.failure
        success.add_condition(Condition.CHANCE, amount_or_quantity=percent)
        for child, trigger in [(n.left, success), (n.right, failure)]:
            assert child
            trigger.add_effect(
                Effect.DEACTIVATE_TRIGGER,
                trigger_id=success.trigger_id
            )
            if isinstance(child.data, int):
                # Swaps the contents of the variable at index 0 with that
                # of the variable at any nonzero index.
                k = child.data
                if k != 0:
                    var_id = current_pieces[k].variable_id
                    trigger.add_effect(
                        Effect.SCRIPT_CALL,
                        message=_swap_msg(var_id0, var_id)
                    )
            else:
                nodes.append(child)
                for t in [child.data.success, child.data.failure]:
                    trigger.add_effect(
                        Effect.ACTIVATE_TRIGGER,
                        trigger_id = t.trigger_id
                    )


def _impl_rand_trees(tdata: TetrisData, tmgr: TMgr):
    """Implements the random tree triggers used in Fisher Yates."""
    for tree in tdata.rand_int_trees:
        for t in (tree.data.success, tree.data.failure):
            tdata.activate_random.add_effect(
                Effect.ACTIVATE_TRIGGER,
                trigger_id=t.trigger_id
            )
        _impl_rand_tree(tdata, tmgr, tree)


def _test_impl_piece_display(tdata: TetrisData, tmgr: TMgr):
    """
    Implements the triggers for testing the Fisher-Yates Tetromino permutation.
    """
    current_vars = tdata.piece_vars[0]
    main_loop_trigger, create_triggers = tdata._test_piece_triggers
    main_loop_trigger.add_condition(Condition.TIMER, timer=5)
    for p in PLAYERS[2:]:
        main_loop_trigger.add_effect(
            Effect.REMOVE_OBJECT,
            source_player = p,
            area_1_x=FY_TEST_SLOT_X,
            area_1_y=FY_TEST_SLOT_Y,
            area_2_x=FY_TEST_SLOT_X+NUM_TETROMINO-1,
            area_2_y=FY_TEST_SLOT_Y
        )
    main_loop_trigger.add_effect(
        Effect.ACTIVATE_TRIGGER,
        trigger_id=tdata.activate_random.trigger_id
    )
    _impl_rand_trees(tdata, tmgr)
    for s, slot_lst in enumerate(create_triggers):
        var_id = current_vars[s].variable_id
        for p, t in enumerate(slot_lst):
            p_index = p+2
            # TODO Fisher Yates randomization, need to change declaration order
            main_loop_trigger.add_effect(
                Effect.ACTIVATE_TRIGGER,
                trigger_id=t.trigger_id
            )
            # Checks the Variable is set to the corresponding player.
            t.add_condition(
                Condition.VARIABLE_VALUE,
                amount_or_quantity=p_index,
                variable=var_id,
                comparison=Comparison.EQUAL
            )
            player = Player(p_index)
            t.add_effect(
                Effect.CREATE_OBJECT,
                object_list_unit_id=PLAYER_TETROMINO[player],
                source_player=player,
                location_x=FY_TEST_SLOT_X + s,
                location_y=FY_TEST_SLOT_Y,
                facet=4
            )
            # Deactivates all triggers in the same slot
            for slot_trigger in slot_lst:
                t.add_effect(
                    Effect.DEACTIVATE_TRIGGER,
                    trigger_id=slot_trigger.trigger_id
                )


def impl_triggers(tdata: TetrisData, mmgr: MMgr, tmgr: TMgr, umgr: UMgr):
    """Implements triggers using the data initialized in `tdata`."""
    _impl_game_loop(tdata)
    _impl_hotkeys(tdata)
    _impl_piece_vars(tdata, tmgr)
    _impl_objectives(tdata, tmgr)
    # _test_impl_piece_display(tdata, tmgr)


def build(args):
    """
    Builds the Tetris scenario file.

    Parameters:
        args: Command-line options passed to affect scenario generation. TBD.
    """
    # TODO this is broken, update when library is fixed 11
    # scn = AoE2Scenario.create_default()
    # This is broken too...
    # scn = AoE2Scenario.from_file('src-scns/default-scenario.aoe2scenario')

    # Use this example scenario for now.
    # Eventually set the player metadata in this code instead of in the editor.
    scn = AoE2Scenario.from_file('src-scns/tetris-base.aoe2scenario')
    umgr = scn.unit_manager
    tmgr = scn.trigger_manager
    mmgr = scn.map_manager

    # Builds the scenario in 2 phases:
    # 1. Define map and player info, place units, and declare triggers.
    # 2. Implement triggers.
    variables = Variables(tmgr)
    tdata = TetrisData(mmgr, tmgr, umgr)
    impl_triggers(tdata, mmgr, tmgr, umgr)

    scn.write_to_file(output_path())


def scratch(_args):
    """Scratch function for executing tests."""
    print('grassDauT')
    print(PLAYERS)


def main():
    """Runs the scenario building application."""
    parser = argparse.ArgumentParser(description='Creates the Tetris scenario.')
    subparser = parser.add_subparsers(help='Subprograms')

    parser_build = subparser.add_parser(
        'build',
        help='Standard build command to create the Tetris.aoe2scenario file.'
    )
    parser_build.set_defaults(func=build)

    parser_scratch = subparser.add_parser(
        'scratch',
        help="Whatever mad experiment T-West's mind has devised."
    )
    parser_scratch.set_defaults(func=scratch)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
