---
name: sublimate-distiller
description: Mine Claude Code session history for repeated tool-call patterns and emit candidate Workflow scripts or Skills. Use when the user says distill workflows, find workflows in my sessions, sublimate, what patterns are in my history, surface repeatable orchestrations, or invokes /sublimate:distill. Walks ~/.claude/projects/, clusters sessions via k-shingle Jaccard, mines frequent subsequences via PrefixSpan, dispatches per-cluster prompt distillation, emits .workflow.js or SKILL.md candidates classified by 3-tier rubric (Subagent / Skill / Workflow).
allowed-tools: Read Bash Grep Glob Write Edit Task
---

# Sublimate Distiller

Mine the current project's Claude Code session corpus, cluster by tool-call similarity, classify, distill, emit candidates.

## Stage 1 — Scope

Determine the session corpus path:

- Default: `~/.claude/projects/$(basename "$PWD" | sed 's|/|-|g; s|^|-|; s|$||')` — Claude Code encodes the absolute project path as a directory under `~/.claude/projects/` using `-` as the separator.
- Override: if `$ARGUMENTS` contains `--project-dir <path>`, use that path instead.

Verify the directory exists and contains `.jsonl` files. Abort with a clear message if empty.

## Stage 2 — Mine

Run the Python miner as a Bash subprocess:

```bash
mkdir -p /tmp/sublimate-run
cd "${CLAUDE_PLUGIN_ROOT}/src" && python3 -m sublimate.cli <projects-dir> \
  --out /tmp/sublimate-run/ \
  --max-sessions 500 \
  --emit-all
```

Run as a module (`python3 -m sublimate.cli`) from inside the `src/` directory so Python resolves `from . import cluster, emit, parser, prefixspan, shingle` relative imports. Invoking the script path directly (`python3 path/to/cli.py`) raises `ImportError: attempted relative import with no known parent package`.

The miner walks JSONL files, extracts `(role, tool_name, tool_input_hash)` per turn, computes k=3 shingles, runs union-find on Jaccard >= 0.35, then PrefixSpan on each cluster.

Output: `/tmp/sublimate-run/clusters.json` (array of cluster records) plus raw `cluster-<id>.workflow.js` skeletons.

## Stage 3 — Curate

Dispatch the `cluster-curator` agent via the Task tool. The agent prompt MUST include both:

- the path to `/tmp/sublimate-run/clusters.json` (dict keyed by cluster id)
- the projects directory determined in Stage 1 (so the curator can resolve `<sample_session_id>.jsonl` → absolute path)

The curator reads ≥ 1 sample session per cluster from `<projects_dir>/<sample_id>.jsonl` and writes `/tmp/sublimate-run/curation.json` with one record per cluster:

```json
{
  "id": "<cluster-id>",
  "verdict": "KEEP | SKIP | NEEDS_MORE_SIGNAL",
  "tier": "NOISE | SUBAGENT | SKILL | WORKFLOW",
  "rationale": "<sentence citing the sample session>",
  "sample_cited": "<jsonl path>"
}
```

Wait for the curator envelope before advancing.

## Stage 4 — Distill prompts

For each cluster where `verdict == KEEP`, dispatch the `prompt-distiller` agent with:

- cluster id
- tier
- 2-3 sample session jsonl paths from the curation record

Distiller reads samples, identifies the procedure, writes a coherent `meta.name` plus per-phase `agent({prompt})` body. Overwrites the raw skeleton at `/tmp/sublimate-run/cluster-<id>.workflow.js` for Workflow tier, or writes `/tmp/sublimate-run/cluster-<id>/SKILL.md` for Skill tier.

Fan out distillers in parallel — one Task call per KEEP cluster in a single assistant message. Do NOT set `run_in_background: true`.

## Stage 5 — Emit

After all distillers return, finalize artifacts under `/tmp/sublimate-run/`:

- `cluster-<id>.workflow.js` for Workflow-tier candidates
- `cluster-<id>/SKILL.md` for Skill-tier candidates
- `cluster-<id>/AGENT.md` for Subagent-tier candidates (sketch only)

SKIP and NEEDS_MORE_SIGNAL clusters are not emitted.

## Stage 6 — Lint

Reject any emitted `.workflow.js` that contains the banned non-determinism substrings. Build the regex at runtime so this skill body itself does not contain the literal:

```bash
BANNED=$(printf '%s|%s|%s' \
  'D''ate.now' \
  'M''ath.random' \
  'new ''Date()')
for f in /tmp/sublimate-run/cluster-*.workflow.js; do
  if grep -E "$BANNED" "$f" >/dev/null; then
    echo "REJECT $f — non-deterministic API detected"
    rm "$f"
  fi
done
```

Workflows must be reproducible. Non-determinism breaks the deterministic-checkpoint guarantee.

## Stage 7 — Report

Print a final table to the user:

```
Cluster   Size  Tier      Verdict   File
-------   ----  ----      -------   ----
c-001     12    WORKFLOW  KEEP      /tmp/sublimate-run/cluster-c-001.workflow.js
c-002     7     SKILL     KEEP      /tmp/sublimate-run/cluster-c-002/SKILL.md
c-003     3     -         SKIP      -
```

Plus the count of emitted files per tier, and a one-line next-step: "Promote a candidate with `/sublimate:promote <cluster-id>`."

## 3-tier classification rubric

- **Subagent** — single repeated role, no orchestration, no fan-out. Cheapest runtime. Emit as `agents/<name>.md`.
- **Skill** — repeated single-phase procedure that needs scoped tools + context. Medium runtime. Emit as `skills/<name>/SKILL.md`.
- **Workflow** — multi-phase, fan-out, deterministic checkpoints, repeated >= 5 times with consistent phase shape. Highest runtime requirements (Claude Code v2.1.154+, Pro/Max/Team/Enterprise). Emit as `.workflow.js`.

When uncertain, prefer Skill over Workflow — Workflows carry more runtime constraints.
