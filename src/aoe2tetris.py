"""
Command line application to build the scenario files for Aoe2 Tetris.

Uses the scenario file parsing library found here:
https://github.com/ksneijders/aoe2scenarioparser
"""


from __future__ import annotations
from AoE2ScenarioParser.aoe2_scenario import AoE2Scenario
from AoE2ScenarioParser.datasets.buildings import Building
from AoE2ScenarioParser.datasets.conditions import Condition
from AoE2ScenarioParser.datasets.effects import Effect
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.trigger_lists import (
    Comparison,
    ObjectAttribute,
    Operation,
)
from AoE2ScenarioParser.datasets.units import Unit
from AoE2ScenarioParser.objects.trigger_obj import TriggerObject
from action import Action
from typing import List
from direction import Direction
from hotkeys import HOTKEY_BUILDINGS
from index import Index
from probtree import ProbTree
from tetrisdata import TetrisData
from tetromino import Tetromino
from variables import Variables
from xscalls import ScriptCaller
import argparse
import os.path


SCN_EXT = "aoe2scenario"  # Scenario file extension.
OUT_SCN_DIR = "out-scns"  # Output directory for built files.
OUT_FILENAME = "Tetris"  # Name of the main scenario.

DIRECTIONS = list(Direction)  # List of all direction constants.
PLAYERS = list(Player)  # List of all player constants.
TETROMINOS = list(Tetromino)  # List of all Tetris piece shapes.

TETRIS_ROWS = 40  # The number of rows in a game of tetris.
TETRIS_COLS = 10  # The number of columns in a game of tetris.
NUM_VISIBLE = 20  # The number of visible rows in the Board.
INIT_ROW = 19  # One row above the first visible row.
INIT_COL = 4  # Left-center column.

SQUARE_SPACE = 1.0  # The amount of space between Tetris game squares.

BUILDING_X = 2  # The x-coordinate to place "select all hotkey" buildings.
BUILDING_Y = 2  # The y-coordinate to place "select all hotkey" buildings.

# Maps a player slot to the string name of that player's color.
PLAYER_COLOR_NAMES = {
    Player.TWO: "Red",
    Player.THREE: "Green",
    Player.FOUR: "Yellow",
    Player.FIVE: "Cyan",
    Player.SIX: "Purple",
    Player.SEVEN: "Blue",
    Player.EIGHT: "Orange",
}

# Maps a player number to the associated Tetromino unit id.
PLAYER_TETROMINO = {
    Player.TWO: Unit.ELITE_BERSERK,
    Player.THREE: Unit.ELITE_HUSKARL,
    Player.FOUR: Unit.ELITE_THROWING_AXEMAN,
    Player.FIVE: Unit.ELITE_TEUTONIC_KNIGHT,
    Player.SIX: Unit.ELITE_SAMURAI,
    Player.SEVEN: Unit.ELITE_WOAD_RAIDER,
    Player.EIGHT: Unit.ELITE_LONGBOWMAN,
}


_XS_MESSAGE_GLOBAL = 0  # Hack to make each xs function have its own name.


def output_path() -> str:
    """Returns the output path for the generated scenario file."""
    return os.path.join(OUT_SCN_DIR, f"{OUT_FILENAME}.{SCN_EXT}")


def _impl_init_invisible_object_ownership(tdata: TetrisData):
    """Implements converting the game board from Player one to Gaia."""
    tdata.init_scenario.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.ONE,
        target_player=Player.GAIA,
        selected_object_ids=[
            tdata.board[Index(r, c)][d].reference_id  # type: ignore
            for r in range(NUM_VISIBLE, tdata.board.num_rows)
            for c in range(tdata.board.num_cols)
            for d in DIRECTIONS
        ],
    )


def _impl_place_initial_piece(
    variables: Variables, tdata: TetrisData, xs: ScriptCaller
):
    """
    Implements placing the initial piece on the game board.

    Required: the Tetromino sequences are randomized.
    """
    for tetromino, trigger in tdata.place_init_piece.items():
        tdata.begin_game.add_effect(
            Effect.ACTIVATE_TRIGGER, trigger_id=trigger.trigger_id
        )
        trigger.add_condition(
            Condition.SCRIPT_CALL,
            xs_function=xs.seq_value_equals(0, tetromino.value),
        )
        for t in list(Tetromino):
            if t != tetromino:
                trigger.add_effect(
                    Effect.DEACTIVATE_TRIGGER,
                    trigger_id=tdata.place_init_piece[t].trigger_id,
                )
        center = Index(INIT_ROW + 1, INIT_COL)
        trigger.add_effect(
            Effect.CHANGE_VARIABLE,
            quantity=center.row,
            from_variable=variables.row.var_id,
            operation=Operation.SET,
        )
        trigger.add_effect(
            Effect.CHANGE_VARIABLE,
            quantity=center.col,
            from_variable=variables.col.var_id,
            operation=Operation.SET,
        )
        trigger.add_effect(
            Effect.CHANGE_VARIABLE,
            quantity=Direction.U.value,
            from_variable=variables.facing.var_id,
            operation=Operation.SET,
        )
        for index in tetromino.indices():
            point = index + center
            if tdata.board.is_visible(point):
                tile_unit = tdata.board[point][Direction.U]  # type: ignore
                trigger.add_effect(
                    Effect.REPLACE_OBJECT,
                    source_player=Player.GAIA,
                    target_player=tetromino.player,
                    selected_object_ids=tile_unit.reference_id,
                    object_list_unit_id_2=tetromino.unit,
                )


def _impl_begin_game(variables: Variables, tdata: TetrisData, xs: ScriptCaller):
    """
    Implents the trigger to initialize the game and begin the game loop.

    Beginning a new game:
    * Sets the Score to 0.
    * Displays the score as an objective.
    * Randomizes the beginning 2 sequences of Tetrominos.
    * Sets the Tetromino sequence index to 0.
    * Sets the game board to be empty.
    * Places the first active piece on the game board.
    """
    t = tdata.begin_game

    # Handles the hotkey press for starting the game.
    university_id = tdata.hotkeys.building_map[Building.UNIVERSITY].reference_id
    t.add_condition(Condition.OBJECT_SELECTED, unit_object=university_id)
    t.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.ONE,
        target_player=Player.GAIA,
        selected_object_ids=university_id,
    )
    t.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.GAIA,
        target_player=Player.ONE,
        selected_object_ids=university_id,
    )

    init_vars = []
    init_vars.append(variables.score)
    for row in variables.board_tiles:
        for v in row:
            init_vars.append(v)
    for v in variables.sequences:
        init_vars.append(v)
    init_vars.append(variables.seq_index)
    for v in init_vars:
        t.add_effect(
            Effect.CHANGE_VARIABLE,
            quantity=v.init,
            operation=Operation.SET,
            from_variable=v.var_id,
        )

    t.add_effect(
        Effect.DEACTIVATE_TRIGGER,
        trigger_id=tdata.new_game_objective.trigger_id,
    )
    t.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.score_objective.trigger_id
    )
    _impl_rand_trees(0, tdata.seq_init0, t, xs)
    _impl_rand_trees(1, tdata.seq_init1, t, xs)
    _impl_place_initial_piece(variables, tdata, xs)

    t.add_effect(Effect.ACTIVATE_TRIGGER, trigger_id=tdata.game_loop.trigger_id)


def _impl_move_left(
    variables: Variables,
    tdata: TetrisData,
    xs: ScriptCaller,
):
    """Implements the left movement trigger."""
    left = tdata.action_triggers[Action.MOVE_LEFT]
    left.add_condition(Condition.SCRIPT_CALL, xs_function=xs.can_move_left())
    # The effects:
    #   * moves the row to the left (script call)
    #   * clears units of the previous active piece
    #   * sets units of the new active piece

    left.add_effect(
        Effect.CHANGE_VARIABLE,
        quantity=1,
        from_variable=variables.row.var_id,
        operation=Operation.SUBTRACT,
    )

    # left_indices = t.indices(d, index)
    # left_adjacent = Index.adjacent_indices(left_indices, Direction.L)
    # for neighbor in left_adjacent:
    #     for u in tdata.board[neighbor].values():
    #         left.add_condition(
    #             Condition.CAPTURE_OBJECT,
    #             unit_object=u.reference_id,
    #             source_player=Player.GAIA
    #         )

    # for original_index in left_indices:
    #     left.add_effect(
    #         Effect.REPLACE_OBJECT,
    #         source_player=t.player.value,
    #         target_player=Player.GAIA.value,
    #         object_list_unit_id_2=Unit.INVISIBLE_OBJECT,
    #         selected_object_ids=tdata.board[original_index][d].reference_id,
    #     )
    # for original_index in left_indices:
    #     new_index = original_index + Direction.L.offset
    #     left.add_effect(
    #         Effect.REPLACE_OBJECT,
    #         source_player=Player.GAIA.value,
    #         target_player=t.player.value,
    #         object_list_unit_id_2=t.unit,
    #         selected_object_ids=tdata.board[new_index][d].reference_id,
    #     )


def _impl_move_right(
    variables: Variables,
    tdata: TetrisData,
    xs: ScriptCaller,
):
    """Implements the right movement trigger."""
    right = tdata.action_triggers[Action.MOVE_RIGHT]
    right.add_condition(Condition.SCRIPT_CALL, xs_function=xs.can_move_right())
    # TODO implement


def _impl_rotate_clockwise(
    variables: Variables,
    tdata: TetrisData,
    xs: ScriptCaller,
):
    """Implements the clockwise rotation trigger."""
    clock = tdata.action_triggers[Action.ROTATE_CLOCKWISE]
    clock.add_condition(
        Condition.SCRIPT_CALL, xs_function=xs.can_rotate_clockwise()
    )
    # TODO implement


def _impl_rotate_counterclockwise(
    variables: Variables,
    tdata: TetrisData,
    xs: ScriptCaller,
):
    """Implements the counterclockwise rotation trigger."""
    counter = tdata.action_triggers[Action.ROTATE_COUNTERCLOCKWISE]
    counter.add_condition(
        Condition.SCRIPT_CALL, xs_function=xs.can_rotate_counterclockwise()
    )
    # TODO implement


def _impl_soft_drop(
    variables: Variables,
    tdata: TetrisData,
    xs: ScriptCaller,
):
    """Implements the soft drop trigger."""
    soft = tdata.action_triggers[Action.SOFT_DROP]
    soft.add_condition(Condition.SCRIPT_CALL, xs_function=xs.can_soft_drop())
    # TODO implement


def _impl_hard_drop(
    variables: Variables,
    tdata: TetrisData,
    xs: ScriptCaller,
):
    """Implements the hard drop trigger."""
    hard = tdata.action_triggers[Action.HARD_DROP]
    hard.add_condition(Condition.SCRIPT_CALL, xs_function=xs.can_hard_drop())
    # TODO implement


def _impl_hold(
    variables: Variables,
    tdata: TetrisData,
    xs: ScriptCaller,
):
    """Implements the hard drop trigger."""
    hold = tdata.action_triggers[Action.HOLD]
    hold.add_condition(Condition.SCRIPT_CALL, xs_function=xs.can_hold())
    # TODO implement


def _impl_new_game(
    variables: Variables,
    tdata: TetrisData,
    xs: ScriptCaller,
):
    """Implements the trigger for starting a new game."""
    new_game = tdata.action_triggers[Action.NEW_GAME]
    new_game.add_condition(
        Condition.VARIABLE_VALUE,
        amount_or_quantity=Action.NEW_GAME.value,
        variable=variables.selected.var_id,
        comparison=Comparison.EQUAL,
    )
    # TODO implement


def _impl_action_triggers(
    variables: Variables, tdata: TetrisData, xs: ScriptCaller
):
    """Implements the triggers for actions a player may take."""
    for at in tdata.action_triggers.values():
        tdata.game_loop.add_effect(
            Effect.ACTIVATE_TRIGGER, trigger_id=at.trigger_id
        )
        tdata.cleanup.add_effect(
            Effect.DEACTIVATE_TRIGGER, trigger_id=at.trigger_id
        )
    _impl_move_left(variables, tdata, xs)
    _impl_move_right(variables, tdata, xs)
    _impl_rotate_clockwise(variables, tdata, xs)
    _impl_rotate_counterclockwise(variables, tdata, xs)
    _impl_soft_drop(variables, tdata, xs)
    _impl_hard_drop(variables, tdata, xs)
    _impl_hold(variables, tdata, xs)


def _impl_game_loop(variables: Variables, tdata: TetrisData, xs: ScriptCaller):
    """Implements the main game loop trigger."""
    tdata.game_loop.add_effect(
        Effect.CHANGE_VARIABLE,
        quantity=0,
        operation=Operation.SET,
        from_variable=variables.selected.var_id,
    )

    selection_triggers = list(tdata.selection_triggers.values())
    for t in selection_triggers:
        tdata.game_loop.add_effect(
            Effect.ACTIVATE_TRIGGER, trigger_id=t.trigger_id
        )

    # Building Selected
    for b, t in tdata.selection_triggers.items():
        bid = tdata.hotkeys.building_map[b].reference_id
        t.add_condition(Condition.OBJECT_SELECTED, unit_object=bid)
        t.add_effect(
            Effect.CHANGE_VARIABLE,
            quantity=HOTKEY_BUILDINGS[b].value,
            operation=Operation.SET,
            from_variable=variables.selected.var_id,
        )
        for src, tar in [(Player.ONE, Player.GAIA), (Player.GAIA, Player.ONE)]:
            t.add_effect(
                Effect.CHANGE_OWNERSHIP,
                source_player=src,
                target_player=tar,
                selected_object_ids=bid,
            )
    for i in range(len(selection_triggers) - 1):
        for j in range(i + 1, len(selection_triggers)):
            selection_triggers[i].add_effect(
                Effect.DEACTIVATE_TRIGGER,
                trigger_id=selection_triggers[j].trigger_id,
            )

    _impl_action_triggers(variables, tdata, xs)

    tdata._game_loop.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.cleanup.trigger_id
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
                object_attributes=ObjectAttribute.LINE_OF_SIGHT,
            )
    tdata.init_scenario.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.GAIA,
        target_player=Player.ONE,
        selected_object_ids=[
            b.reference_id for b in tdata.hotkeys.building_map.values()
        ],
    )


def _impl_objectives(variables: Variables, tdata: TetrisData):
    """Implements the triggers to initialize and display player score."""
    objectives = [
        tdata.new_game_objective,
        tdata.score_objective,
    ] + tdata.debug_objectives
    for obj in objectives:
        obj.add_condition(Condition.PLAYER_DEFEATED, source_player=Player.GAIA)


def _impl_rand_tree(seq_index: int, tree: ProbTree, xs: ScriptCaller):
    """
    Implements the triggers for `tree`.

    Requires that `tree` stores `ChanceNode` data (not `int` data).
    Requires that the root `tree` node's `success` and `failure` triggers
        are activated by a trigger that occurs in `tmgr`'s trigger list
        before any of the `success` or `failure` triggers in the tree.
    """
    nodes = [tree]  # The internal tree nodes with triggers to implement.
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
                Effect.DEACTIVATE_TRIGGER, trigger_id=success.trigger_id
            )
            if isinstance(child.data, int):
                # Swaps the contents of the variable at index 0 with that
                # of the variable at any nonzero index.
                if child.data != 0:
                    trigger.add_effect(
                        Effect.SCRIPT_CALL,
                        message=xs.swap_digits(seq_index, 0, child.data),
                    )
            else:
                nodes.append(child)
                for t in [child.data.success, child.data.failure]:
                    trigger.add_effect(
                        Effect.ACTIVATE_TRIGGER, trigger_id=t.trigger_id
                    )


def _impl_rand_trees(
    seq_index: int,
    seq: List[ProbTree],
    activator: TriggerObject,
    xs: ScriptCaller,
):
    """
    Implements the random tree triggers used in Fisher Yates.

    seq_index: `0` or `1` to indicate which Tetromino sequence to randomize.
    """
    for tree in seq:
        for t in (tree.data.success, tree.data.failure):
            activator.add_effect(
                Effect.ACTIVATE_TRIGGER, trigger_id=t.trigger_id
            )
        _impl_rand_tree(seq_index, tree, xs)


def impl_triggers(variables: Variables, tdata: TetrisData):
    """Implements triggers using the data initialized in `tdata`."""
    xs = ScriptCaller(variables)
    _impl_init_invisible_object_ownership(tdata)
    _impl_hotkeys(variables, tdata)
    _impl_begin_game(variables, tdata, xs)
    _impl_game_loop(variables, tdata, xs)
    _impl_objectives(variables, tdata)


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
    scn = AoE2Scenario.from_file("src-scns/tetris-base.aoe2scenario")
    umgr = scn.unit_manager
    tmgr = scn.trigger_manager
    mmgr = scn.map_manager

    # Builds the scenario in 2 phases:
    # 1. Define map and player info, place units, and declare triggers.
    # 2. Implement triggers.
    variables = Variables(tmgr)
    tdata = TetrisData(
        mmgr,
        tmgr,
        umgr,
        variables,
        BUILDING_X,
        BUILDING_Y,
        TETRIS_ROWS,
        TETRIS_COLS,
        SQUARE_SPACE,
    )
    impl_triggers(variables, tdata)

    scn.write_to_file(output_path())


def scratch(_args):
    """Scratch function for executing tests."""
    print("grassDauT")


def main():
    """Runs the scenario building application."""
    parser = argparse.ArgumentParser(description="Creates the Tetris scenario.")
    subparser = parser.add_subparsers(help="Subprograms")

    parser_build = subparser.add_parser(
        "build",
        help="Standard build command to create the Tetris.aoe2scenario file.",
    )
    parser_build.set_defaults(func=build)

    parser_scratch = subparser.add_parser(
        "scratch", help="Whatever mad experiment T-West's mind has devised."
    )
    parser_scratch.set_defaults(func=scratch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
