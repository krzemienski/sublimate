---
name: workflow-authoring
description: Take a cluster spec and author a polished .workflow.js with real agent() prompts distilled from sample sessions. Use when sublimate-distiller dispatches per cluster, or when user says author workflow, polish this cluster, distill prompts from sessions, or invokes /sublimate:author-workflow with a cluster ID.
allowed-tools: Read Write Edit
---

# Workflow Authoring

Given a cluster id and 2-3 sample session paths, produce a polished `.workflow.js` (Workflow tier) or `SKILL.md` (Skill tier) at `/tmp/sublimate-run/cluster-<id>.workflow.js` or `/tmp/sublimate-run/cluster-<id>/SKILL.md`.

## Inputs

- `cluster_id` — string
- `tier` — `WORKFLOW` or `SKILL`
- `samples` — array of 2-3 absolute paths to `.jsonl` session files
- `skeleton_path` — `/tmp/sublimate-run/cluster-<id>.workflow.js` (PrefixSpan raw output)

## Procedure

1. **Read samples.** Open every sample path. Focus on user messages, tool sequences, and final assistant turns. The tool sequence alone is insufficient — read what the user actually wanted accomplished.
2. **Name.** Choose `meta.name` as a short verb-noun (`generate-cover`, `audit-fix-verify`, `mine-weekly-retro`). Avoid generics like `do-thing`.
3. **Phase.** Group tool calls into goal-oriented phases. Each phase has one goal — `audit`, `fix`, `verify`, `emit`, etc. Boundaries are determined by goal change, not by tool change.
4. **Author prompts.** For each phase write a coherent `agent({prompt})` that generalizes — not a verbatim replay of the sample. The polished prompt should work for the next run, not just past runs.
5. **Fan-out.** Any phase with N independent units gets `parallel()`. Default to serial; only parallelize when independence is provable from samples.
6. **Deterministic only.** No wall-clock (`Date.now`), no RNG (`Math.random`), no `new Date()`. Use `meta.id` plus inputs for any keying.

## Output

Overwrite the skeleton:

- Workflow tier → `/tmp/sublimate-run/cluster-<id>.workflow.js`
- Skill tier → `/tmp/sublimate-run/cluster-<id>/SKILL.md`

Return a short report:

```
output: <path>
summary: <one line describing what the workflow/skill does>
samples_read: [<path1>, <path2>, ...]
```
