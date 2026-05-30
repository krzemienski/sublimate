# Sublimate Architecture

## Why a plugin, not a CLI

v0.1.0 shipped as a Python CLI (`workflow-distill`). v0.2.0 wraps that CLI in a Claude Code plugin so the user-facing surface is the slash command and skill set, not the bin script.

The pivot:

- **Discovery.** Users find Sublimate through `claude plugin marketplace` and slash command listing, not through PyPI.
- **Composition.** Sublimate dispatches its own sub-agents (cluster-curator, prompt-distiller) using Claude's `Task` tool. A standalone CLI cannot.
- **Surface area.** The Python miner becomes plugin-internal — invoked via Bash inside the skill body. Users never type `python3`.

## How it composes

```
User: /sublimate:distill
  ↓
commands/distill.md  →  invokes Skill tool
  ↓
skills/sublimate-distiller/SKILL.md
  ↓ Stage 2: Bash
  python3 ${CLAUDE_PLUGIN_ROOT}/src/sublimate/cli.py ...
  ↓ /tmp/sublimate-run/clusters.json
  ↓ Stage 3: Task
  agents/cluster-curator.md  →  /tmp/sublimate-run/curation.json
  ↓ Stage 4: Task (per KEEP cluster)
  agents/prompt-distiller.md  →  polished .workflow.js or SKILL.md
  ↓ Stage 6: Bash (lint)
  ↓ Stage 7: report
User reviews → /sublimate:promote <cluster-id>
  ↓
commands/promote.md  →  moves artifact into project's .claude/
```

## File map

```
sublimate/
├── .claude-plugin/
│   ├── plugin.json          # manifest (v0.2.0)
│   └── marketplace.json     # distribution descriptor
├── skills/
│   ├── sublimate-distiller/SKILL.md   # main entry; orchestrates 7 stages
│   └── workflow-authoring/SKILL.md    # sub-skill for polishing one cluster
├── commands/
│   ├── distill.md           # /sublimate:distill — entry point
│   ├── show.md              # /sublimate:show — list candidates
│   └── promote.md           # /sublimate:promote — move into project
├── agents/
│   ├── cluster-curator.md   # classify clusters by tier
│   └── prompt-distiller.md  # polish prompts from samples
├── src/sublimate/           # Python miner (unchanged from v0.1.0)
│   ├── cli.py               # entry point; called by skill via Bash
│   ├── parser.py            # JSONL walker
│   ├── shingle.py           # k-shingle generator
│   ├── cluster.py           # union-find on Jaccard
│   ├── prefixspan.py        # frequent subsequence miner
│   └── emit.py              # Jinja → .workflow.js
├── docs/
│   └── ARCHITECTURE.md      # this file
├── pyproject.toml           # still publishable to PyPI for advanced users
└── README.md                # plugin install instructions first; pip second
```

## Tier classification

The skill emits three tiers. Choosing the right tier matters because each has different runtime constraints:

- **Subagent**: single repeated role. Lowest runtime cost. Emit as `agents/<name>.md`.
- **Skill**: single-phase procedure with context + tool-scope needs. Medium runtime. Emit as `skills/<name>/SKILL.md`.
- **Workflow**: multi-phase, fan-out, checkpoints. Highest runtime requirements (Claude Code v2.1.154+, Pro/Max/Team/Enterprise). Emit as `.workflow.js`.

When uncertain, prefer Skill. Workflows are reserved for procedures the user has run ≥5 times with consistent phase structure.

## Deterministic-only invariant

The Stage 6 lint rejects any emitted `.workflow.js` containing `Date.now`, `Math.random`, or `new Date()`. Workflows must be reproducible — non-determinism breaks the deterministic-checkpoint guarantee that makes Workflow tier worth the runtime cost.
