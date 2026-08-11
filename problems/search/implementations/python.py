"""PROB-SEARCH-001: repeated membership lookup.

Reference implementation variants for evidence-driven comparison.
These functions deliberately use Python's standard data structures rather
than custom containers unless the experiment specifically studies one.
"""

from bisect import bisect_left
from collections.abc import Iterable


def linear_contains(values: list[int], target: int) -> bool:
    return target in values


def binary_contains(sorted_values: list[int], target: int) -> bool:
    index = bisect_left(sorted_values, target)
    return index < len(sorted_values) and sorted_values[index] == target


def build_hash_index(values: Iterable[int]) -> set[int]:
    return set(values)


def hash_contains(index: set[int], target: int) -> bool:
    return target in index


def validate_unique(values: list[int]) -> None:
    if len(values) != len(set(values)):
        raise ValueError("PROB-SEARCH-001 requires unique identifiers")
