"""Classes for managing hotkey selection in the Tetris scenario."""


from AoE2ScenarioParser.datasets.buildings import Building
from AoE2ScenarioParser.datasets.players import Player
from AoE2ScenarioParser.objects.units_obj import UnitsObject as UMgr
from action import Action


# Maps the building id of a select all building hotkey to the actions that
# selecting the building performs.
HOTKEY_BUILDINGS = {
    Building.ARCHERY_RANGE: Action.MOVE_LEFT,
    Building.BLACKSMITH: Action.MOVE_RIGHT,
    Building.STABLE: Action.ROTATE_CLOCKWISE,
    Building.KREPOST: Action.ROTATE_COUNTERCLOCKWISE,
    Building.MONASTERY: Action.SOFT_DROP,
    Building.CASTLE: Action.HARD_DROP,
    Building.SIEGE_WORKSHOP: Action.HOLD,
    Building.UNIVERSITY: Action.NEW_GAME,
}


class HotkeyBuildings:
    """An instance contains the buildings used for selection triggers."""

    def __init__(self, umgr: UMgr, x: int, y: int):
        """
        Adds buildings to the scenario for use in the selection triggers.

        `(x, y)` is the coordinate where buildings are placed on the map.
        """
        self._building_map = {
            b: umgr.add_unit(player=Player.GAIA, unit_const=b, x=x, y=y)
            for b in HOTKEY_BUILDINGS.keys()
        }

    @property
    def building_map(self):
        """Returns a mapping from a building id to the unit paced on the map."""
        return self._building_map

    def x(self):
        """Returns the x tile coordinate where the buildings are located."""
        return self._x

    def y(self):
        """Returns the y tile coordinate where the buildings are located."""
        return self._y
