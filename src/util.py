"""Various utility functions."""


from typing import Any, List
import random


def fisher_yates(lst: List[Any]):
    """Randomly permutes `lst` in place."""
    n = len(lst) - 1
    # lst[0:i] is permuted randomly.
    for i in range(n):
        j = random.randint(i, n)
        lst[i], lst[j] = lst[j], lst[i]
