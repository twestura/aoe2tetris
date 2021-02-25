"""A tree structure for creating chance trigger sequences."""


from AoE2ScenarioParser.objects.trigger_obj import TriggerObject
from btreenode import BTreeNode
from typing import Union


class ChanceNode:
    """
    A node in a probability tree representing a Chance and two paths.

    The `percent` is the integer chance from `0` to `100` of succeeding the
    Chance condition and choosing the left branch, with the right branch being
    chosen on failure.
    """

    def __init__(
        self, percent: int, success: TriggerObject, failure: TriggerObject
    ):
        """
        Constructs a new ChanceNode.

        Parameters:
            percent: The chance of succeeding the Chance condition.
            success: The trigger to activate when the Chance succeeds.
            failure: The trigger to activate when the Chance fails.

        Raises:
            ValueError: If `percent` is not within `0` to `100`, inclusive.
        """
        if percent < 0 or 100 < percent:
            raise ValueError(f"{percent} must be in `0--100`, inclusive.")
        self._percent = percent
        self._success = success
        self._failure = failure

    @property
    def percent(self) -> int:
        """Returns the percent for the Chance condition."""
        return self._percent

    @property
    def success(self) -> TriggerObject:
        """Returns the success trigger for passing the Chance condition."""
        return self._success

    @property
    def failure(self) -> TriggerObject:
        """Returns the failure trigger for failing the Chance condition."""
        return self._failure


# A binary tree storing `TriggerObject`s or `int`s for generating random `int`s.
ProbTree = BTreeNode[Union[ChanceNode, int]]
