"""Union-find clustering of sessions by Jaccard similarity on shingle sets."""

from .shingle import jaccard


def _find(parent: dict, x: str) -> str:
    root = x
    while parent[root] != root:
        root = parent[root]
    # Path compression
    while parent[x] != root:
        parent[x], x = root, parent[x]
    return root


def _union(parent: dict, a: str, b: str) -> None:
    ra = _find(parent, a)
    rb = _find(parent, b)
    if ra != rb:
        parent[ra] = rb


def cluster_sessions(
    session_shingles: dict[str, set],
    threshold: float = 0.35,
) -> dict[int, list[str]]:
    """Cluster sessions by Jaccard similarity on shingle sets.

    Args:
        session_shingles: Map of session_id to shingle set.
        threshold: Minimum Jaccard similarity to union two sessions.

    Returns:
        Map of cluster_id (int starting at 0) to list of session_ids.
        Singleton clusters are filtered out.
    """
    session_ids = list(session_shingles.keys())
    parent = {sid: sid for sid in session_ids}

    n = len(session_ids)
    for i in range(n):
        for j in range(i + 1, n):
            sid_a = session_ids[i]
            sid_b = session_ids[j]
            sim = jaccard(session_shingles[sid_a], session_shingles[sid_b])
            if sim >= threshold:
                _union(parent, sid_a, sid_b)

    # Group by root
    groups: dict[str, list[str]] = {}
    for sid in session_ids:
        root = _find(parent, sid)
        groups.setdefault(root, []).append(sid)

    # Filter singletons and renumber starting at 0
    result: dict[int, list[str]] = {}
    cluster_id = 0
    for members in groups.values():
        if len(members) >= 2:
            result[cluster_id] = members
            cluster_id += 1

    return result
