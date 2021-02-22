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
from typing import Any, Dict, List, Tuple, Union
from btreenode import BTreeNode
from hotkeys import HotkeyBuildings, HOTKEY_BUILDINGS
from probtree import ChanceNode, ProbTree
from tetrisdata import TetrisData
from tetromino import Tetromino
from variables import ScnVar, Variables
import argparse
import math
import os.path
import random


# Trigger headers for testing Fisher Yates.
# The first element is a trigger for running a test loop.
# The second element is a `Tetromino.num()` by `Tetromino.num()` list indexed
# by debug slot and then player colo.
# TODO add the Fisher Yates randomization triggers along with the loop and
# the create object triggers.
Test_FY_Triggers = Tuple[TriggerObject, List[List[TriggerObject]]]


SCN_EXT = 'aoe2scenario' # Scenario file extension.
OUT_SCN_DIR = 'out-scns' # Output directory for built files.
OUT_FILENAME = 'Tetris' # Name of the main scenario.

PLAYERS = list(Player) # List of all player constants.

TETRIS_ROWS = 20 # The number of rows in a game of tetris.
TETRIS_COLS = 10 # The number of columns in a game of tetris.

SQUARE_SPACE = 1.0 # The amount of space between Tetris game squares.

BUILDING_X = 2 # The x-coordinate to place "select all hotkey" buildings.
BUILDING_Y = 2 # The y-coordinate to place "select all hotkey" buildings.

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
    return [_declare_prob_tree(tmgr, n)
            for n in range(Tetromino.num()-1, 0, -1)]


def _declare_test_piece_triggers(tmgr: TMgr) -> Test_FY_Triggers:
    """TODO specify, testing function."""
    main_loop = tmgr.add_trigger('Randomize And Place Test Row', looping=True)
    triggers = [[None] * Tetromino.num() for __ in range(Tetromino.num())]
    for k in range(Tetromino.num()):
        for (p, player) in enumerate(PLAYERS[2:]):
            color = PLAYER_COLOR_NAMES[player]
            triggers[k][p] = tmgr.add_trigger(
                f'Place {color} in slot {k}',
                enabled=False
            )
    return (main_loop, triggers)


def _impl_begin_game(variables: Variables, tdata: TetrisData):
    """
    Implents the trigger to initialize the game and begin the game loop.

    Beginning a new game:
    * Sets the Score to 0.
    * Displays the score as an objective.
    * Randomizes the beginning 2 sequences of Tetrominos.
    * Sets the Tetromino sequence index to 0.
    * Places the first piece on the game board.
    """
    t = tdata.begin_game
    university_id = tdata.hotkeys.building_map[Building.UNIVERSITY].reference_id
    t.add_condition(Condition.OBJECT_SELECTED, unit_object=university_id)
    t.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.ONE,
        target_player=Player.GAIA,
        selected_object_ids=university_id
    )
    t.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.GAIA,
        target_player=Player.ONE,
        selected_object_ids=university_id
    )
    t.add_effect(
        Effect.CHANGE_VARIABLE,
        quantity=variables.score.init,
        from_variable=variables.score.var_id,
        operation=Operation.SET
    )
    t.add_effect(
        Effect.DEACTIVATE_TRIGGER,
        trigger_id=tdata.new_game_objective.trigger_id
    )
    t.add_effect(
        Effect.ACTIVATE_TRIGGER,
        trigger_id=tdata.score_objective.trigger_id
    )
    t.add_effect(
        Effect.ACTIVATE_TRIGGER,
        trigger_id=tdata.game_loop.trigger_id
    )


def _impl_game_loop(variables: Variables, tdata: TetrisData):
    """Implements the main game loop trigger."""
    tdata.game_loop.add_effect(
        Effect.CHANGE_VARIABLE,
        quantity=0,
        operation=Operation.SET,
        from_variable=variables.selected.var_id
    )

    selection_triggers = list(tdata.selection_triggers.values())
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
    for b, t in tdata.selection_triggers.items():
        bid = tdata.hotkeys.building_map[b].reference_id
        t.add_condition(
            Condition.OBJECT_SELECTED,
            unit_object=bid
        )
        t.add_effect(
            Effect.CHANGE_VARIABLE,
            quantity=HOTKEY_BUILDINGS[b].value,
            operation=Operation.SET,
            from_variable=variables.selected.var_id
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

    tdata._game_loop.add_effect(
        Effect.ACTIVATE_TRIGGER,
        trigger_id=tdata.cleanup.trigger_id
    )


def _impl_hotkeys(variables: Variables, tdata: TetrisData):
    """
    Implements the building selection hotkeys and variables.

    Buildings begin under the Gaia player's control.
    The line of sight of these buildings is set to 0 for both GAIA and
    player ONE.
    Ownerships of the buildings is transferred to player ONE once this
    line of sight is set.
    This ordering prevents the buildings from appearing on the map as
    visible to player ONE.
    """
    for b in HOTKEY_BUILDINGS.keys():
        for p in (Player.GAIA, Player.ONE):
            tdata.init_scenario.add_effect(
                Effect.MODIFY_ATTRIBUTE,
                quantity=0,
                object_list_unit_id=b,
                source_player=p,
                operation=Operation.SET,
                object_attributes=ObjectAttribute.LINE_OF_SIGHT
            )
    tdata.init_scenario.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.GAIA,
        target_player=Player.ONE,
        selected_object_ids=[
            b.reference_id for b in tdata.hotkeys.building_map.values()
        ]
    )


def _impl_objectives(variables: Variables, tdata: TetrisData, tmgr: TMgr):
    """Implements the triggers to initialize and display player score."""
    tdata.new_game_objective.add_condition(
        Condition.PLAYER_DEFEATED,
        source_player=Player.GAIA
    )
    tdata.score_objective.add_condition(
        Condition.PLAYER_DEFEATED,
        source_player=Player.GAIA
    )


def _impl_rand_tree(
        variables: Variables,
        tdata: TetrisData,
        tmgr: TMgr,
        tree: ProbTree):
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
            area_2_x=FY_TEST_SLOT_X+Tetromino.num()-1,
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


def impl_triggers(
        variables: Variables,
        tdata: TetrisData,
        mmgr: MMgr,
        tmgr: TMgr,
        umgr: UMgr):
    """Implements triggers using the data initialized in `tdata`."""
    _impl_begin_game(variables, tdata)
    _impl_game_loop(variables, tdata)
    _impl_hotkeys(variables, tdata)
    # _impl_piece_vars(variables, tdata, tmgr)
    _impl_objectives(variables, tdata, tmgr)
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
    tdata = TetrisData(mmgr, tmgr, umgr, variables.score,
                       BUILDING_X, BUILDING_Y,
                       TETRIS_ROWS, TETRIS_COLS, SQUARE_SPACE)
    impl_triggers(variables, tdata, mmgr, tmgr, umgr)

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
