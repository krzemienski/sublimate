"""K-shingle utilities for tool sequences."""

from __future__ import annotations


def shingle(tools: list[str], k: int = 3) -> set[tuple[str, ...]]:
    """Return set of k-tuples of consecutive tool names.

    Filters None/empty strings before shingling. If filtered sequence is
    shorter than k, returns one shingle padded with '<pad>'.
    """
    filtered = [t for t in tools if t]

    if len(filtered) < k:
        padded = filtered + ["<pad>"] * (k - len(filtered))
        return {tuple(padded)}

    return {tuple(filtered[i : i + k]) for i in range(len(filtered) - k + 1)}


def jaccard(a: set, b: set) -> float:
    """Return |a ∩ b| / |a ∪ b|. Returns 0.0 if both empty."""
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)
