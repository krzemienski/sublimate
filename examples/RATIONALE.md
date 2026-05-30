# examples/ rationale

These four specimens were produced by a live `/sublimate:distill` dogfood run against the `blog-series` corpus on 2026-05-28 — the full skill chain (mine → cluster-curator → per-cluster prompt-distiller → lint → report), not a direct Python miner call. Every specimen cites a verifiable sample session under `~/.claude/projects/-Users-nick-Desktop-blog-series/`. The full run transcript, curation envelope, and Stage 7 report are archived in the blog-series repo under `plans/260528-2330-sublimate-v0.2-pivot/.audit/`.

A previous trio (`post-cover.workflow.js`, `audit-verify-ship.workflow.js`, `weekly-retro.workflow.js`) was synthetic scaffolding written before any mining. It was deleted. An interim set distilled by a direct miner call (without the curator/distiller agents) was also replaced by these — the ones below are the canonical dogfood output.

## The run

| Field | Value |
|---|---|
| Corpus | `blog-series` (500 of 2,067 sessions sampled) |
| Clusters found | 17 |
| Candidates emitted | 8 (6 SKILL + 1 SUBAGENT + 1 WORKFLOW) |
| Skipped | 5 SKIP, 4 NEEDS_MORE_SIGNAL |
| Python miner runtime | 1.36s |
| Full chain wall-clock | ~10m 28s |

Full classification of all 8 KEEP candidates lives in `../SPECIMENS.json`.

---

## 1. `dream-memory-consolidation-SKILL.md` — SKILL

**Origin:** blog-series cluster 1, 361 sessions.
**Sample cited:** `018eeda4-fbb2-4f94-a1f1-7240da424dcf.jsonl`.
**Why SKILL:** the `/dream` memory-consolidation procedure (Orient → Gather → Consolidate → Prune), recurring across 361 sessions, `ls` + `Read` + `grep` + `Write` against the project memory dir. A coherent multi-phase procedure Claude orchestrates turn-by-turn, intermediate state in context — Skill tier, not background-script Workflow.

Note: a naive shape-only miner reads cluster 1 as a generic `Bash → Bash` noise cluster and discards it. The cluster-curator agent read a sample session, recognized the `/dream` procedure, and kept it. That is the entire value of the curator layer.

## 2. `parallel-file-write-with-verify.workflow.js` — WORKFLOW

**Origin:** blog-series cluster 9, 6 sessions.
**Sample cited:** `239ce6ee-467a-4437-914d-1cb51260c640/subagents/workflows/wf_5176ec98-1e1/agent-a72dccfcec0c806fe.jsonl`.
**Why WORKFLOW:** parent workflows that scatter N writer-subagent spawns in parallel, then run a verify pass that reads each written file and emits a metrics table. Multi-phase fan-out + checkpoint, repeated 6×. The only Workflow-tier specimen the blog-series corpus produced. WORKFLOW requires multi-phase fan-out repeated 5+ times; cluster 9 has exactly that.

## 3. `file-writer-worker-SUBAGENT.md` — SUBAGENT

**Origin:** blog-series cluster 8, 12 sessions.
**Sample cited:** `239ce6ee-467a-4437-914d-1cb51260c640/subagents/workflows/wf_20d2bf84-f00/agent-a12d5a2eb14aef09a.jsonl`.
**Why SUBAGENT:** twelve sibling workers spawned by a parent workflow, each writing exactly one file. Single repeated role, no orchestration, no phase boundary, tools needed: `Write`. Canonical Task-tool one-shot. If forced to WORKFLOW the runtime would wrap a single-task pattern in a checkpoint scaffold for nothing — the rubric pulls it to the lighter tier where it belongs.

## 4. `audit-e2e-SKILL.md` — SKILL

**Origin:** blog-series cluster 11, 6 sessions.
**Sample cited:** `30bd71d4-536b-4608-9db2-b7c61ea9a5f9/subagents/agent-a0e6cf9fa2bece81b.jsonl`.
**Why SKILL:** the chrome-devtools e2e-audit team worker. Five user journeys per teammate, per-journey `new_page → take_screenshot → take_snapshot → click via uid → close_page`. The distiller extracted the `new_page → list_pages → select_page → snapshot` about:blank pitfall, five common journey shapes, and a FAIL protocol from two real team-trial transcripts. Sequential per-journey, intermediate state fits Claude's context — Skill, not Workflow.

Cluster 11 has three parallel siblings the miner also surfaced and kept — cluster 12 (`audit-a11y`), cluster 13 (`audit-perf`), cluster 14 (`audit-responsive`). Same fan-out shape, four audit dimensions. See `../SPECIMENS.json`.

---

## What got rejected

The miner + curator flagged 9 of 17 clusters as not worth emitting:

- **5 SKIP (NOISE):** `/remote-control` bridge-session bookkeeping (cluster 6, 22 sessions), auto-compact resume continuations, and other incidental tool co-occurrence with no coherent procedure across samples.
- **4 NEEDS_MORE_SIGNAL:** coherent shapes that appeared only 2–3 times — `episodic-memory:search` subagent (cluster 2), a skills-reader team worker (cluster 7) — kept on the bench until more sessions accumulate.

The miner proposes; the curator reads samples and decides; you curate the final set. Eight candidates surfaced, four earned a place in `examples/`. That ratio is the point.
