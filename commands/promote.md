---
description: Promote a sublimate candidate to your project's .claude/workflows/ or .claude/skills/.
---

# /sublimate:promote <cluster-id>

Promote a candidate from `/tmp/sublimate-run/` into the current project's `.claude/` tree.

## Procedure

1. Read `/tmp/sublimate-run/curation.json`. Find the record with `id == $ARGUMENTS`.
2. Determine destination based on tier:
   - `WORKFLOW` — copy `/tmp/sublimate-run/cluster-<id>.workflow.js` to `.claude/workflows/<slug>.workflow.js` (slug from `meta.name`).
   - `SKILL` — copy `/tmp/sublimate-run/cluster-<id>/SKILL.md` to `.claude/skills/<name>/SKILL.md`.
   - `SUBAGENT` — copy `/tmp/sublimate-run/cluster-<id>/AGENT.md` to `.claude/agents/<name>.md`.
3. If the destination file already exists, ask the user to confirm overwrite. Do NOT overwrite silently.
4. After the copy, print the destination path and a one-line next-step:
   - Workflow → `Run with /workflows`
   - Skill → `Invoke with /<name>` or via natural-language trigger
   - Subagent → `Spawn via Task tool`

Reject if `$ARGUMENTS` is empty or the cluster has `verdict != KEEP`.
