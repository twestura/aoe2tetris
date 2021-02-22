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


SCN_EXT = 'aoe2scenario' # Scenario file extension.
OUT_SCN_DIR = 'out-scns' # Output directory for built files.
OUT_FILENAME = 'Tetris' # Name of the main scenario.

PLAYERS = list(Player) # List of all player constants.

TETRIS_ROWS = 40 # The number of rows in a game of tetris.
TETRIS_COLS = 10 # The number of columns in a game of tetris.
NUM_VISIBLE = 0.5 * TETRIS_ROWS # The number of visible rows in the Board.
INIT_ROW = 19
INIT_COL = 4

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


def _impl_place_initial_piece(variables: Variables, tdata: TetrisData):
    """
    Implements placing the initial piece on the game board.

    Required: the Tetromino sequences are randomized.
    """
    for tetromino, trigger in tdata.place_init_piece.items():
        tdata.begin_game.add_effect(
            Effect.ACTIVATE_TRIGGER,
            trigger_id=trigger.trigger_id
        )
        trigger.add_condition(
            Condition.VARIABLE_VALUE,
            amount_or_quantity=tetromino.value,
            variable=variables.tseq[0].var_id,
            comparison=Comparison.EQUAL
        )
        for t in list(Tetromino):
            if t != tetromino:
                trigger.add_effect(
                    Effect.DEACTIVATE_TRIGGER,
                    trigger_id=tdata.place_init_piece[t].trigger_id
                )
        tile_unit = tdata.board[INIT_ROW + 1][INIT_COL]
        trigger.add_effect(
            Effect.REPLACE_OBJECT,
            source_player=Player.GAIA,
            target_player=tetromino.player,
            selected_object_ids=tile_unit.reference_id,
            object_list_unit_id_2=tetromino.unit
        )
        # TODO just places the center for now, needs to fill the other
        # tiles as well


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

    # Sets Tetromino Variable Values.
    for v in variables.tseq:
        t.add_effect(
            Effect.CHANGE_VARIABLE,
            quantity=v.init,
            operation=Operation.SET,
            from_variable=v.var_id
        )
    t.add_effect(
            Effect.CHANGE_VARIABLE,
            quantity=variables.seq_index.init,
            operation=Operation.SET,
            from_variable=variables.seq_index.var_id
    )

    _impl_rand_trees(variables, tdata.seq_init0, t)
    t.add_effect(
        Effect.ACTIVATE_TRIGGER,
        trigger_id=tdata.swap_init.trigger_id
    )
    for k in range(Tetromino.num()):
        tdata.swap_init.add_effect(
            Effect.SCRIPT_CALL,
            message=_swap_msg(
                variables.tseq[k].var_id,
                variables.tseq[k+Tetromino.num()].var_id
            ),
        )
    _impl_rand_trees(variables, tdata.seq_init1, t)

    _impl_place_initial_piece(variables, tdata)

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
        tree: ProbTree):
    """
    Implements the triggers for `tree`.

    Requires that `tree` stores `ChanceNode` data (not `int` data).
    Requires that the root `tree` node's `success` and `failure` triggers
        are activated by a trigger that occurs in `tmgr`'s trigger list
        before any of the `success` or `failure` triggers in the tree.
    """
    current_pieces = variables.tseq[:Tetromino.num()]
    var_id0 = current_pieces[0].var_id
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
                    var_id = current_pieces[k].var_id
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


def _impl_rand_trees(
        variables: Variables,
        seq: List[PropTree],
        activator: TriggerObject):
    """Implements the random tree triggers used in Fisher Yates."""
    for tree in seq:
        for t in (tree.data.success, tree.data.failure):
            activator.add_effect(
                Effect.ACTIVATE_TRIGGER,
                trigger_id=t.trigger_id
            )
        _impl_rand_tree(variables, tree)


def impl_triggers(
        variables: Variables,
        tdata: TetrisData,
        mmgr: MMgr,
        tmgr: TMgr,
        umgr: UMgr):
    """Implements triggers using the data initialized in `tdata`."""
    tdata.init_scenario.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.ONE,
        target_player=Player.GAIA,
        selected_object_ids=[
            unit.reference_id
            for row in tdata.board
            for unit in row
        ]
    )
    _impl_hotkeys(variables, tdata)
    _impl_begin_game(variables, tdata)
    _impl_game_loop(variables, tdata)
    _impl_objectives(variables, tdata, tmgr)


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
