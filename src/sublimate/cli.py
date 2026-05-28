"""CLI driver: parser -> shingle -> cluster -> prefixspan -> emit."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

from . import cluster, emit, parser, prefixspan, shingle


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sublimate")
    ap.add_argument("projects_dir", type=Path)
    ap.add_argument("--out", type=Path, default=Path("./out"))
    ap.add_argument("--max-sessions", type=int, default=None)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--jaccard", type=float, default=0.35)
    ap.add_argument("--min-support", type=float, default=0.4)
    ap.add_argument("--emit-all", action="store_true", default=False)
    args = ap.parse_args(argv)

    projects_dir: Path = args.projects_dir
    if not projects_dir.exists():
        print(f"ERROR: projects_dir does not exist: {projects_dir}", file=sys.stderr)
        return 2

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    # Parse sessions
    t0 = time.perf_counter()
    session_tools: dict[str, list[str]] = {}
    tool_histogram: Counter = Counter()

    for session_id, events in parser.iter_sessions(projects_dir, max_sessions=args.max_sessions):
        tools = [
            e.tool_name
            for e in events
            if e.role == "assistant" and e.tool_name
        ]
        session_tools[session_id] = tools
        tool_histogram.update(tools)

    parse_time = time.perf_counter() - t0

    parse_report = {
        "session_count": len(session_tools),
        "tool_histogram": dict(tool_histogram.most_common()),
        "parse_time_seconds": parse_time,
    }
    (out_dir / "parse.json").write_text(json.dumps(parse_report, indent=2))

    # Shingle
    session_shingles: dict[str, set] = {
        sid: shingle.shingle(tools, k=args.k) for sid, tools in session_tools.items()
    }

    # Cluster
    clusters = cluster.cluster_sessions(session_shingles, threshold=args.jaccard)

    # PrefixSpan per cluster
    cluster_report: dict[str, dict] = {}
    cluster_patterns: dict = {}

    for cluster_id, members in clusters.items():
        sequences = [session_tools[sid] for sid in members]
        patterns = prefixspan.prefix_span(
            sequences, min_support_ratio=args.min_support
        )
        cluster_patterns[cluster_id] = (members, patterns)
        cluster_report[str(cluster_id)] = {
            "size": len(members),
            "sample_session_ids": list(members[:5]),
            "top_patterns": [
                {"pattern": list(p), "support": s} for p, s in patterns[:10]
            ],
        }

    (out_dir / "clusters.json").write_text(json.dumps(cluster_report, indent=2))

    # Emit workflows
    emitted_files: list[Path] = []
    if args.emit_all:
        for cluster_id, (members, patterns) in cluster_patterns.items():
            size = len(members)
            if size < 3 or len(patterns) < 2:
                continue

            phases = []
            for i, (pat, _support) in enumerate(patterns):
                first_token = pat[0] if pat else "step"
                phases.append(
                    {
                        "title": f"phase-{i}-{first_token}",
                        "detail": " -> ".join(pat),
                        "agents": [
                            {
                                "label": f"step-{i}",
                                "prompt": "Execute pattern: " + " -> ".join(pat),
                            }
                        ],
                    }
                )

            top_pattern = patterns[0][0]
            workflow = {
                "name": "cluster-" + str(cluster_id),
                "description": (
                    "Distilled from "
                    + str(size)
                    + " sessions. Top pattern: "
                    + " -> ".join(top_pattern)
                ),
                "phases": phases,
            }

            out_path = out_dir / f"cluster-{cluster_id}.workflow.js"
            emit.render_workflow(
                name=workflow["name"],
                description=workflow["description"],
                phases=workflow["phases"],
                out_path=out_path,
            )
            emitted_files.append(out_path)

        for path in emitted_files:
            warnings = emit.lint_emitted(path)
            for w in warnings:
                print(f"LINT {path.name}: {w}", file=sys.stderr)

    # Summary
    print(f"Parsed {len(session_tools)} sessions in {parse_time:.2f}s")
    print(f"Clusters: {len(clusters)}")
    print()
    print(f"{'cluster':<10} {'size':<6} {'support':<8} top-pattern")
    print("-" * 70)
    for cid, info in cluster_report.items():
        top = info["top_patterns"][0] if info["top_patterns"] else None
        if top:
            pat_str = " -> ".join(top["pattern"])
            print(f"{cid:<10} {info['size']:<6} {top['support']:<8} {pat_str}")
        else:
            print(f"{cid:<10} {info['size']:<6} {'-':<8} (no patterns)")
    print()
    print(f"Emitted {len(emitted_files)} workflow files to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
