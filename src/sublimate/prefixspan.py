"""Minimal PrefixSpan implementation for mining frequent sequential patterns.

Vendored from the standard PrefixSpan algorithm description (Pei et al., 2001).
Stdlib only.
"""

from collections import Counter
from typing import Optional


def _frequent_items(projected_db: list[list[str]], min_support: int) -> list[tuple[str, int]]:
    """Count items occurring in projected sequences (once per sequence)."""
    counts: Counter[str] = Counter()
    for seq in projected_db:
        seen: set[str] = set()
        for item in seq:
            if item in seen:
                continue
            seen.add(item)
            counts[item] += 1
    return [(item, c) for item, c in counts.items() if c >= min_support]


def _project(projected_db: list[list[str]], item: str) -> list[list[str]]:
    """Build projected database for the given item.

    For each sequence containing item, take the suffix after first occurrence.
    """
    result: list[list[str]] = []
    for seq in projected_db:
        for idx, val in enumerate(seq):
            if val == item:
                result.append(seq[idx + 1:])
                break
    return result


def _mine(
    projected_db: list[list[str]],
    prefix: tuple[str, ...],
    min_support: int,
    max_pattern_len: int,
    patterns: list[tuple[tuple[str, ...], int]],
) -> None:
    """Recursive PrefixSpan mining step."""
    if len(prefix) >= max_pattern_len:
        return

    for item, support in _frequent_items(projected_db, min_support):
        new_prefix = prefix + (item,)
        if len(new_prefix) >= 2:
            patterns.append((new_prefix, support))
        if len(new_prefix) >= max_pattern_len:
            continue
        new_db = _project(projected_db, item)
        if not new_db:
            continue
        _mine(new_db, new_prefix, min_support, max_pattern_len, patterns)


def prefix_span(
    sequences: list[list[str]],
    min_support: Optional[int] = None,
    min_support_ratio: float = 0.4,
    max_pattern_len: int = 6,
) -> list[tuple[tuple[str, ...], int]]:
    """Mine frequent sequential patterns via PrefixSpan.

    Args:
        sequences: list of input sequences (each a list of item strings).
        min_support: absolute minimum support count. If None, derived from
            min_support_ratio as max(2, int(min_support_ratio * len(sequences))).
        min_support_ratio: fraction of sequences for derived min_support.
        max_pattern_len: maximum pattern length to mine.

    Returns:
        list of (pattern tuple, support_count) sorted by support DESC,
        containing only patterns of length >= 2.
    """
    if not sequences:
        return []

    if min_support is None:
        min_support = max(2, int(min_support_ratio * len(sequences)))

    patterns: list[tuple[tuple[str, ...], int]] = []
    _mine(sequences, (), min_support, max_pattern_len, patterns)

    patterns.sort(key=lambda p: p[1], reverse=True)
    return patterns
