from __future__ import annotations

from collections.abc import Iterable


def total(values: Iterable[int | float] | None) -> int | float:
    if values is None:
        return 0
    return sum(values)
