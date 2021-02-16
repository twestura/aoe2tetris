"""
Command line application to build the scenario files for Aoe2 Tetris.

Uses the scenario file parsing library found here:
https://github.com/ksneijders/aoe2scenarioparser
"""


from AoE2ScenarioParser.aoe2_scenario import AoE2Scenario
from AoE2ScenarioParser.datasets.buildings import Building
from AoE2ScenarioParser.datasets.conditions import Condition
from AoE2ScenarioParser.datasets.effects import Effect
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.datasets.units import Unit
from AoE2ScenarioParser.objects.map_obj import MapObject
from AoE2ScenarioParser.objects.unit_obj import UnitObject
from AoE2ScenarioParser.objects.trigger_obj import TriggerObject
import argparse
import math
import os.path


SCN_EXT = 'aoe2scenario' # Scenario file extension.
OUT_SCN_DIR = 'out-scns' # Output directory for built files.
OUT_FILENAME = 'Tetris' # Name of the main scenario.

# List of all player constants.
PLAYERS = [p for p in Player]


TETRIS_ROWS = 20 # The number of rows in a game of tetris.
TETRIS_COLS = 10 # The number of columns in a game of tetris.
SQUARE_SPACE = 1.0 # The amount of space between Tetris game squares.

BUILDING_X = 2
BUILDING_Y = 2


def output_path():
    """Returns the output path for the generated scenario file."""
    return os.path.join(OUT_SCN_DIR, f'{OUT_FILENAME}.{SCN_EXT}')


def _place_invisible_objects(umgr):
    """Places invisible objects in the left corner of the map."""
    for p in PLAYERS:
        if p != Player.GAIA:
            umgr.add_unit(
                player=p,
                unit_const=Unit.INVISIBLE_OBJECT,
                x=0,
                y=0,
            )


def _generate_game_board(mmgr, umgr):
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


def _generate_hotkey_presses(
        mmgr: MapObject,
        tmgr: TriggerObject,
        umgr: UnitObject):
    """
    Generates the buildings and triggers for pressing hotkeys.
    """
    center_x = mmgr.map_width / 2.0 + 0.5
    center_y = mmgr.map_height / 2.0 + 0.5
    rotation = 0.75 * math.pi
    cata = umgr.add_unit(
        player=Player.ONE,
        unit_const=Unit.ELITE_CATAPHRACT,
        x=center_x,
        y=center_y,
        rotation=rotation
    )

    archery0 = umgr.add_unit(
        player=Player.ONE,
        unit_const=Building.ARCHERY_RANGE,
        x=BUILDING_X,
        y=BUILDING_Y
    )
    archery1 = umgr.add_unit(
        player=Player.ONE,
        unit_const=Building.ARCHERY_RANGE,
        x=BUILDING_X,
        y=BUILDING_Y
    )

    barracks0 = umgr.add_unit(
        player=Player.ONE,
        unit_const=Building.BARRACKS,
        x=BUILDING_X,
        y=BUILDING_Y
    )
    barracks1 = umgr.add_unit(
        player=Player.ONE,
        unit_const=Building.BARRACKS,
        x=BUILDING_X,
        y=BUILDING_Y
    )

    buildings_gaia = tmgr.add_trigger('Set Starting Buildings to Gaia')
    building_ids = [barracks1.reference_id, archery1.reference_id]
    buildings_gaia.add_effect(
        Effect.CHANGE_OWNERSHIP,
        selected_object_ids=building_ids,
        source_player=Player.ONE,
        target_player=Player.GAIA,
    )

    select_barracks_0 = tmgr.add_trigger('Move Right 0', looping=True)
    select_barracks_1 = tmgr.add_trigger('Move Right 1', looping=True)
    select_barracks_0.add_condition(
        Condition.OBJECT_SELECTED,
        unit_object=barracks0.reference_id
    )
    select_barracks_0.add_effect(
        Effect.CHANGE_OWNERSHIP,
        selected_object_ids=barracks0.reference_id,
        source_player=Player.ONE,
        target_player=Player.GAIA,
    )
    select_barracks_0.add_effect(
        Effect.CHANGE_OWNERSHIP,
        selected_object_ids=barracks1.reference_id,
        source_player=Player.GAIA,
        target_player=Player.ONE,
    )
    select_barracks_0.add_effect(
        Effect.TELEPORT_OBJECT,
        selected_object_ids=cata.reference_id,
        location_x=73,
        location_y=73,
    )
    select_barracks_1.add_condition(
        Condition.OBJECT_SELECTED,
        unit_object=barracks1.reference_id
    )
    select_barracks_1.add_effect(
        Effect.CHANGE_OWNERSHIP,
        selected_object_ids=barracks1.reference_id,
        source_player=Player.ONE,
        target_player=Player.GAIA,
    )
    select_barracks_1.add_effect(
        Effect.CHANGE_OWNERSHIP,
        selected_object_ids=barracks0.reference_id,
        source_player=Player.GAIA,
        target_player=Player.ONE,
    )
    select_barracks_1.add_effect(
        Effect.TELEPORT_OBJECT,
        selected_object_ids=cata.reference_id,
        location_x=73,
        location_y=73,
    )

    select_archery_0 = tmgr.add_trigger('Move Left 0', looping=True)
    select_archery_1 = tmgr.add_trigger('Move Left 1', looping=True)
    select_archery_0.add_condition(
        Condition.OBJECT_SELECTED,
        unit_object=archery0.reference_id
    )
    select_archery_0.add_effect(
        Effect.CHANGE_OWNERSHIP,
        selected_object_ids=archery0.reference_id,
        source_player=Player.ONE,
        target_player=Player.GAIA,
    )
    select_archery_0.add_effect(
        Effect.CHANGE_OWNERSHIP,
        selected_object_ids=archery1.reference_id,
        source_player=Player.GAIA,
        target_player=Player.ONE,
    )
    select_archery_0.add_effect(
        Effect.TELEPORT_OBJECT,
        selected_object_ids=cata.reference_id,
        location_x=71,
        location_y=71,
    )
    select_archery_1.add_condition(
        Condition.OBJECT_SELECTED,
        unit_object=archery1.reference_id
    )
    select_archery_1.add_effect(
        Effect.CHANGE_OWNERSHIP,
        selected_object_ids=archery1.reference_id,
        source_player=Player.ONE,
        target_player=Player.GAIA,
    )
    select_archery_1.add_effect(
        Effect.CHANGE_OWNERSHIP,
        selected_object_ids=archery0.reference_id,
        source_player=Player.GAIA,
        target_player=Player.ONE,
    )
    select_archery_1.add_effect(
        Effect.TELEPORT_OBJECT,
        selected_object_ids=cata.reference_id,
        location_x=71,
        location_y=71,
    )


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

    _place_invisible_objects(umgr)
    _generate_game_board(mmgr, umgr)
    _generate_hotkey_presses(mmgr, tmgr, umgr)

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
