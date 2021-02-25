"""An implementation of a Binary Tree."""


from __future__ import annotations
from typing import Generic, Optional, TypeVar


T = TypeVar("T")


class BTreeNode(Generic[T]):
    """A Binary Tree Node with data and left and right children."""

    def __init__(
        self,
        data: T,
        left: Optional[BTreeNode[T]] = None,
        right: Optional[BTreeNode[T]] = None,
    ):
        """
        Initializes a new Binary Tree Node.

        `None` assigned to the `left` or `right` instance variables
        represents not having that child.
        """
        self._data = data
        self._left = left
        self._right = right

    @property
    def data(self):
        """Returns the value stored in this node."""
        return self._data

    @property
    def left(self):
        """
        Returns this node's left child, or `None` if there is no left child.
        """
        return self._left

    @property
    def right(self):
        """
        Returns this node's right child, or `None if there is no right child.
        """
        return self._right
