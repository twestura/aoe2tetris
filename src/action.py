"""Represents the set of actions a user may take during a game of Tetris."""


from enum import Enum


class Action(Enum):
    """
    The actions a player may take during a game by pressing hotkeys.

    The int value of each enum is the priority of the enum, with the
    lowest value representing the highest priority.
    """

    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    ROTATE_CLOCKWISE = 3
    ROTATE_COUNTERCLOCKWISE = 4
    SOFT_DROP = 5
    HARD_DROP = 6
    HOLD = 7
    NEW_GAME = 8

    def __str__(self):
        return _STRS[self]


# Maps each action to its string representation.
_STRS = {
    Action.MOVE_LEFT: 'Move Left',
    Action.MOVE_RIGHT: 'Move Right',
    Action.ROTATE_CLOCKWISE: 'Rotate Clockwise',
    Action.ROTATE_COUNTERCLOCKWISE: 'Rotate Counterclockwise',
    Action.SOFT_DROP: 'Soft Drop',
    Action.HARD_DROP: 'Hard Drop',
    Action.HOLD: 'Hold',
    Action.NEW_GAME: 'New Game',
}
