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
    AttackStance,
    ObjectAttribute,
    Operation,
)
from AoE2ScenarioParser.datasets.units import Unit
from AoE2ScenarioParser.objects.trigger_obj import TriggerObject
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

SQUARE_SPACE_V = 1.2  # The amount of vertical space between rows.
SQUARE_SPACE_H = 0.9  # The amount of horizontal space between columns.

BUILDING_X = 2  # The x-coordinate to place "select all hotkey" buildings.
BUILDING_Y = 2  # The y-coordinate to place "select all hotkey" buildings.


PLACEHOLDER = Unit.INVISIBLE_OBJECT  # The unit used for board tiles.


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
    Player.THREE: Unit.ELITE_EAGLE_WARRIOR,
    Player.FOUR: Unit.ELITE_JAGUAR_WARRIOR,
    Player.FIVE: Unit.ELITE_TEUTONIC_KNIGHT,
    Player.SIX: Unit.ELITE_SAMURAI,
    Player.SEVEN: Unit.ELITE_WOAD_RAIDER,
    Player.EIGHT: Unit.ELITE_HUSKARL,
}


def output_path() -> str:
    """Returns the output path for the generated scenario file."""
    return os.path.join(OUT_SCN_DIR, f"{OUT_FILENAME}.{SCN_EXT}")


def _impl_init_invisible_object_ownership(tdata: TetrisData):
    """Implements converting the game board from Player one to Gaia."""
    units = []
    for tile in tdata.board.visible():
        for u in tile.values():
            units.append(u)
    for board in tdata.next_units:
        for row in board:
            for u in row:
                units.append(u)
    for row in tdata.hold_units:
        for u in row:
            units.append(u)
    tdata.init_scenario.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.ONE,
        target_player=Player.GAIA,
        selected_object_ids=([u.reference_id for u in units]),
    )


def _impl_no_attack_stance(tdata: TetrisData):
    """Adds an initialization effect to set all units to No Attack Stance."""
    for p in PLAYERS:
        tdata.init_scenario.add_effect(
            Effect.CHANGE_OBJECT_STANCE,
            source_player=p,
            attack_stance=AttackStance.NO_ATTACK_STANCE,
        )


def _impl_range(tdata: TetrisData):
    """
    Adds initialization effects to give 100 range to Invisible Objects and to
    the units used as Tetrominos for all players.
    """
    for p in PLAYERS:
        for t in range(Tetromino.num() + 1):
            u = Tetromino.from_int(t).unit if t else PLACEHOLDER
            tdata.init_scenario.add_effect(
                Effect.MODIFY_ATTRIBUTE,
                quantity=100,
                object_list_unit_id=u,
                source_player=p,
                operation=Operation.SET,
                object_attributes=ObjectAttribute.MAX_RANGE,
            )


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
                        message=xs.swap_seq_values(seq_index, 0, child.data),
                    )
            else:
                nodes.append(child)
                for t in [child.data.success, child.data.failure]:
                    trigger.add_effect(
                        Effect.ACTIVATE_TRIGGER, trigger_id=t.trigger_id
                    )


def _impl_rand_trees(
    tdata: TetrisData,
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
            if seq_index == 1:
                tdata.shuffle.add_effect(
                    Effect.ACTIVATE_TRIGGER, trigger_id=t.trigger_id
                )
        _impl_rand_tree(seq_index, tree, xs)


def _impl_render_triggers(tdata: TetrisData, xs: ScriptCaller):
    """
    Implements the individual tile and direction unit replacement triggers.
    """
    for key, render in tdata.render_triggers.items():
        index, d, t = key
        render.add_condition(
            Condition.SCRIPT_CALL,
            xs_function=xs.can_render_tile(index, d, t),
        )
        p = t.player.value if t else Player.GAIA
        u = t.unit if t else PLACEHOLDER
        tile = tdata.board[index]
        assert tile is not None
        unit_object = tile[d]
        render.add_effect(
            Effect.REPLACE_OBJECT,
            target_player=p,
            object_list_unit_id_2=u,
            selected_object_ids=[unit_object.reference_id],
        )


def _impl_render_next_triggers(tdata: TetrisData, xs: ScriptCaller):
    """Implements the triggers for updating the next unit boards."""
    for index, (trigger_board, unit_board) in enumerate(
        zip(tdata.render_next_triggers, tdata.next_units)
    ):
        all_unit_ids = {u.reference_id for row in unit_board for u in row}
        for t, trigger in enumerate(trigger_board):
            tetromino = Tetromino.from_int(t + 1)
            trigger.add_condition(
                Condition.SCRIPT_CALL,
                xs_function=xs.can_render_next(index, tetromino),
            )
            gaia_id_set = all_unit_ids - tetromino.board_unit_ids(unit_board)
            unit_ids = list(all_unit_ids - gaia_id_set)
            gaia_ids = list(gaia_id_set)
            trigger.add_effect(
                Effect.REPLACE_OBJECT,
                target_player=tetromino.player,
                object_list_unit_id_2=tetromino.unit,
                selected_object_ids=unit_ids,
            )
            trigger.add_effect(
                Effect.REPLACE_OBJECT,
                target_player=Player.GAIA,
                object_list_unit_id_2=PLACEHOLDER,
                selected_object_ids=gaia_ids,
            )


def _impl_render_hold_triggers(tdata: TetrisData, xs: ScriptCaller):
    """Implements the triggers for rendering the hold board."""
    renderInvisible = tdata.render_hold_triggers[0]
    renderInvisible.add_condition(
        Condition.SCRIPT_CALL,
        xs_function=xs.can_render_hold(None),
    )
    all_unit_ids = {u.reference_id for row in tdata.hold_units for u in row}
    renderInvisible.add_effect(
        Effect.REPLACE_OBJECT,
        target_player=Player.GAIA,
        object_list_unit_id_2=PLACEHOLDER,
        selected_object_ids=list(all_unit_ids),
    )

    for t in range(1, Tetromino.num() + 1):
        tetromino = Tetromino.from_int(t)
        trigger = tdata.render_hold_triggers[t]
        trigger.add_condition(
            Condition.SCRIPT_CALL, xs_function=xs.can_render_hold(tetromino)
        )
        gaia_id_set = all_unit_ids - tetromino.board_unit_ids(tdata.hold_units)
        unit_ids = list(all_unit_ids - gaia_id_set)
        gaia_ids = list(gaia_id_set)
        trigger.add_effect(
            Effect.REPLACE_OBJECT,
            target_player=tetromino.player,
            object_list_unit_id_2=tetromino.unit,
            selected_object_ids=unit_ids,
        )
        trigger.add_effect(
            Effect.REPLACE_OBJECT,
            target_player=Player.GAIA,
            object_list_unit_id_2=PLACEHOLDER,
            selected_object_ids=gaia_ids,
        )


def _impl_explosion_triggers(tdata: TetrisData, xs: ScriptCaller):
    """Implements the triggers for exploding rows and clearing the corpses."""
    for r in range(NUM_VISIBLE, TETRIS_ROWS):
        explode = tdata.explode_rows[r]
        clear = tdata.clear_explodes[r]
        explode.add_condition(
            Condition.SCRIPT_CALL, xs_function=xs.can_explode(r)
        )
        clear.add_condition(
            Condition.SCRIPT_CALL, xs_function=xs.can_clear_explode(r)
        )
        clear.add_effect(
            Effect.HEAL_OBJECT,
            quantity=4000,
            object_list_unit_id=Building.FORTIFIED_WALL,
            source_player=Player.GAIA,
        )
        for c in range(TETRIS_COLS):
            for d in DIRECTIONS:
                tile = tdata.board[Index(r, c)]
                assert tile
                attacker = tile[d]
                target = tdata.get_wall(r, c, d)
                explode.add_effect(
                    Effect.TASK_OBJECT,
                    selected_object_ids=[attacker.reference_id],
                    location_object_reference=target.reference_id,
                )
                clear.add_effect(
                    Effect.STOP_OBJECT,
                    selected_object_ids=[attacker.reference_id],
                )
                clear.add_effect(
                    Effect.REPLACE_OBJECT,
                    target_player=Player.GAIA,
                    object_list_unit_id_2=PLACEHOLDER,
                    selected_object_ids=[attacker.reference_id],
                )


def _add_render_trigger_toggles(
    tdata: TetrisData, activator: TriggerObject, deactivator: TriggerObject
):
    """
    Appends effects to activate and deactivate the render triggers.

    Parameters:
        activator: The trigger to which the activate effects are appended.
        deactivator: The trigger to which the deactivate effects are appended.
    """
    triggers = [
        tdata.react_tetris,
        tdata.react_hold,
        tdata.react_hold_fail,
        tdata.react_lock,
        tdata.react_move,
    ]
    for t in tdata.render_triggers.values():
        triggers.append(t)
    for next_list in tdata.render_next_triggers:
        for t in next_list:
            triggers.append(t)
    for t in tdata.render_hold_triggers:
        triggers.append(t)
    for t in tdata.explode_rows.values():
        triggers.append(t)
    for t in tdata.clear_explodes.values():
        triggers.append(t)
    for t in triggers:
        activator.add_effect(Effect.ACTIVATE_TRIGGER, trigger_id=t.trigger_id)
        deactivator.add_effect(
            Effect.DEACTIVATE_TRIGGER, trigger_id=t.trigger_id
        )


def _impl_reaction_sounds(tdata: TetrisData, xs: ScriptCaller):
    """Implements the sounds that play in reaction to various game events."""
    for trigger, xs_function, sound_name in [
        (tdata.react_tetris, xs.can_react_tetris(), "PLAY_TAUNT_30"),
        (tdata.react_move, xs.can_react_move(), "PLAY_VILLAGER_WOOD_CHOP"),
        (tdata.react_hold, xs.can_react_hold(), "PLAY_VILLAGER_MINING"),
        (tdata.react_hold_fail, xs.can_react_hold_fail(), "PLAY_ERROR"),
        (tdata.react_lock, xs.can_react_lock(), "PLAY_WALL_SELECT"),
        (
            tdata._react_game_over,
            xs.can_react_game_over(),
            "PLAY_PLAYER_ELIMINATED",
        ),
        (
            tdata._react_game_over_easter,
            xs.can_react_game_over_easter(),
            "PLAY_TAUNT_27",
        ),
    ]:
        trigger.add_condition(Condition.SCRIPT_CALL, xs_function=xs_function)
        trigger.add_effect(Effect.PLAY_SOUND, sound_name=sound_name)
    tdata._react_game_over_easter.add_effect(
        Effect.SCRIPT_CALL, message=xs.ack_game_over_easter()
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
    can = tdata.can_begin
    # Handles the initial hotkey press for starting the first game.
    university_id = tdata.hotkeys.building_map[Building.UNIVERSITY].reference_id
    can.add_condition(Condition.OBJECT_SELECTED, unit_object=university_id)
    can.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.ONE,
        target_player=Player.GAIA,
        selected_object_ids=university_id,
    )
    can.add_effect(
        Effect.CHANGE_OWNERSHIP,
        source_player=Player.GAIA,
        target_player=Player.ONE,
        selected_object_ids=university_id,
    )
    can.add_effect(
        Effect.DEACTIVATE_TRIGGER,
        trigger_id=tdata.new_game_objective.trigger_id,
    )
    can.add_effect(
        Effect.DEACTIVATE_TRIGGER,
        trigger_id=tdata.game_over_objective.trigger_id,
    )
    can.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.stat_objective.trigger_id
    )
    can.add_effect(Effect.ACTIVATE_TRIGGER, trigger_id=t.trigger_id)

    # Initializes game variables.
    t.add_effect(Effect.SCRIPT_CALL, message=xs.begin_game())

    _impl_rand_trees(tdata, 0, tdata.seq_init0, t, xs)
    _impl_rand_trees(tdata, 1, tdata.seq_init1, t, xs)

    _impl_render_triggers(tdata, xs)
    _impl_render_next_triggers(tdata, xs)
    _impl_render_hold_triggers(tdata, xs)
    _impl_explosion_triggers(tdata, xs)

    tdata.begin_game.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.begin_game_mid.trigger_id
    )
    tdata.begin_game_mid.add_effect(
        Effect.SCRIPT_CALL, message=xs.begin_game_mid()
    )
    _add_render_trigger_toggles(
        tdata, tdata.begin_game_mid, tdata.begin_game_end
    )
    tdata.begin_game_mid.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.begin_game_end.trigger_id
    )
    tdata.begin_game_end.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.game_loop.trigger_id
    )
    tdata.begin_game_end.add_effect(
        Effect.PLAY_SOUND, sound_name="PLAY_WONDER_STARTED"
    )


def _impl_game_loop(variables: Variables, tdata: TetrisData, xs: ScriptCaller):
    """Implements the main game loop trigger."""
    tdata.game_loop.add_effect(Effect.SCRIPT_CALL, message=xs.init_game_loop())
    selection_triggers = list(tdata.selection_triggers.values())
    for t in selection_triggers:
        tdata.game_loop.add_effect(
            Effect.ACTIVATE_TRIGGER, trigger_id=t.trigger_id
        )
    for b, t in tdata.selection_triggers.items():
        bid = tdata.hotkeys.building_map[b].reference_id
        t.add_condition(Condition.OBJECT_SELECTED, unit_object=bid)
        t.add_effect(
            Effect.SCRIPT_CALL,
            message=xs.select_building(HOTKEY_BUILDINGS[b]),
        )
        for src, tar in [(Player.ONE, Player.GAIA), (Player.GAIA, Player.ONE)]:
            t.add_effect(
                Effect.CHANGE_OWNERSHIP,
                source_player=src,
                target_player=tar,
                selected_object_ids=bid,
            )
        for t2 in selection_triggers:
            if t != t2:
                t.add_effect(
                    Effect.DEACTIVATE_TRIGGER, trigger_id=t2.trigger_id
                )
    tdata.game_loop.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.new_game.trigger_id
    )
    tdata.new_game.add_condition(
        Condition.SCRIPT_CALL, xs_function=xs.can_start_new_game()
    )
    tdata.new_game.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.begin_game.trigger_id
    )
    tdata.new_game.add_effect(
        Effect.DEACTIVATE_TRIGGER, trigger_id=tdata.game_loop.trigger_id
    )
    tdata.new_game.add_effect(
        Effect.DEACTIVATE_TRIGGER, trigger_id=tdata.update.trigger_id
    )
    tdata.update.add_effect(
        Effect.DEACTIVATE_TRIGGER, trigger_id=tdata.new_game.trigger_id
    )

    tdata.game_loop.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.update.trigger_id
    )

    tdata.update.add_effect(Effect.SCRIPT_CALL, message=xs.update())
    tdata.update.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.shuffle.trigger_id
    )
    tdata.shuffle.add_condition(Condition.SCRIPT_CALL, xs_function=xs.shuffle())

    _impl_reaction_sounds(tdata, xs)

    tdata.update.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.game_over.trigger_id
    )
    tdata.cleanup.add_effect(
        Effect.DEACTIVATE_TRIGGER, trigger_id=tdata.game_over.trigger_id
    )
    tdata.game_over.add_condition(
        Condition.SCRIPT_CALL, xs_function=xs.is_game_over()
    )
    tdata.game_over.add_effect(
        Effect.DEACTIVATE_TRIGGER, trigger_id=tdata.game_loop.trigger_id
    )
    tdata.game_over.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.game_over_objective.trigger_id
    )
    tdata.game_over.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.can_begin.trigger_id
    )
    _add_render_trigger_toggles(tdata, tdata.update, tdata.cleanup)
    tdata.game_over.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.react_game_over.trigger_id
    )
    tdata.react_game_over.add_effect(
        Effect.DEACTIVATE_TRIGGER,
        trigger_id=tdata.react_game_over_easter.trigger_id,
    )
    tdata.game_over.add_effect(
        Effect.ACTIVATE_TRIGGER,
        trigger_id=tdata.react_game_over_easter.trigger_id,
    )
    tdata.react_game_over_easter.add_effect(
        Effect.DEACTIVATE_TRIGGER, trigger_id=tdata.react_game_over.trigger_id
    )
    tdata.update.add_effect(
        Effect.ACTIVATE_TRIGGER, trigger_id=tdata.cleanup.trigger_id
    )


def _impl_hotkey_initialization(tdata: TetrisData):
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
    for obj in (
        tdata.new_game_objective,
        tdata.stat_objective,
        tdata.game_over_objective,
    ):
        obj.add_condition(Condition.PLAYER_DEFEATED, source_player=Player.GAIA)


def impl_triggers(variables: Variables, tdata: TetrisData):
    """Implements triggers using the data initialized in `tdata`."""
    xs = ScriptCaller()
    tdata.init_scenario.add_effect(
        Effect.SCRIPT_CALL,
        message=xs.init_xs_state(),
    )
    _impl_init_invisible_object_ownership(tdata)
    _impl_no_attack_stance(tdata)
    _impl_range(tdata)
    _impl_objectives(variables, tdata)
    _impl_hotkey_initialization(tdata)
    _impl_begin_game(variables, tdata, xs)
    _impl_game_loop(variables, tdata, xs)


def build(args):
    """
    Builds the Tetris scenario file.

    Parameters:
        args: Command-line options passed to affect scenario generation. TBD.
    """
    scn = AoE2Scenario.from_file("src-scns/tetris-base.aoe2scenario")
    mmgr = scn.map_manager
    tmgr = scn.trigger_manager
    umgr = scn.unit_manager

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
        NUM_VISIBLE,
        SQUARE_SPACE_V,
        SQUARE_SPACE_H,
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
