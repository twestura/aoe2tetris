"""Enum to represent clockwise and counterclockwise rotations."""


from enum import Enum, auto


class Rotation(Enum):
    """An instace representations a 90 degree rotation direction."""

    CW = auto()
    CCW = auto()
