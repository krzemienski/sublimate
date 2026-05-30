# sublimate

> Distill your Claude Code session history into reusable Workflow scripts and Skills. Pattern-mining for agentic engineers.

Status: v0.2.0 — Claude Code plugin shape. Wraps the v0.1.0 Python miner in slash commands + skills + agents. Paired with Anthropic's Dynamic Workflows release at https://claude.com/blog/introducing-dynamic-workflows-in-claude-code (2026-05-28).

## Install (Claude Code plugin)

```bash
claude plugin marketplace add krzemienski/sublimate
claude plugin install sublimate@sublimate-marketplace
```

Then from any project:

```
/sublimate:distill          # mine sessions, emit candidates
/sublimate:show             # review the candidate table
/sublimate:promote <id>     # move a candidate into your project's .claude/
```

See `docs/ARCHITECTURE.md` for how the plugin composes the Python miner with cluster-curator and prompt-distiller agents.

## What it does

Walks JSONL session files in your Claude Code projects directory. Clusters sessions by tool-call similarity (k=3 shingles + Jaccard). Mines frequent subsequences (PrefixSpan) and emits one `.workflow.js` per cluster you can drop into `.claude/workflows/`.

## Why

What serious agent-builders developed by hand for six months — phase boundaries, parallel sub-agent fan-out, scoped tool grants, deterministic checkpoints — is now a Claude Code primitive. The patterns are already sitting in your own session history, waiting to be distilled. This tool reads what you actually did, finds the repeats, and emits scaffolds you can curate into real Workflows. Background: [Anthropic announcement](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code), [Workflows API docs](https://code.claude.com/docs/en/workflows.md).

## Standalone CLI (advanced)

The Python miner is still publishable for direct invocation if you want to bypass the plugin shell:

```bash
git clone https://github.com/krzemienski/sublimate
cd sublimate
pip install -e .
workflow-distill ~/.claude/projects/-Users-nick-Desktop-myproject --out ./out --emit-all
ls out/
```

Python >= 3.10. Single runtime dep: `jinja2`. The plugin (v0.2.0) invokes this same CLI internally via Bash — the plugin is the recommended surface.

## How it works

1. Parser walks `.jsonl` files, extracts `(role, tool_name, tool_input_hash)` per turn.
2. Shingle: `k=3` tool n-grams as sets per session.
3. Cluster: union-find on Jaccard >= 0.35.
4. PrefixSpan: top frequent subsequences per cluster (min support 0.4).
5. Emitter: Jinja to `.workflow.js` with literal `meta` block, `phase()`/`agent()`/`parallel()` body.

## Examples

Four specimens from a live `/sublimate:distill` dogfood run against the blog-series corpus (500 sessions, 2026-05-28). One per tier, plus a second Skill:

- `examples/dream-memory-consolidation-SKILL.md` — SKILL, cluster 1, 361 sessions. The `/dream` memory-consolidation procedure (Orient → Gather → Consolidate → Prune).
- `examples/parallel-file-write-with-verify.workflow.js` — WORKFLOW, cluster 9, 6 sessions. Fan-out N file writers, then a verify pass that audits each file.
- `examples/file-writer-worker-SUBAGENT.md` — SUBAGENT, cluster 8, 12 sessions. Single-role worker: one Write directive, one confirmation token.
- `examples/audit-e2e-SKILL.md` — SKILL, cluster 11, 6 sessions. chrome-devtools per-journey e2e audit worker.

See `examples/RATIONALE.md` for each specimen's origin cluster, sample session, and why it landed at that tier.

## Caveats (v0.2)

- Heuristic, not ML. The algorithm proposes; you curate.
- Dynamic Workflows requires Claude Code v2.1.154+ on Pro / Max / Team / Enterprise. The CLI miner runs anywhere; emitted scripts need that runtime.
- Tool-call patterns are not semantic intent. `Read -> Edit -> Bash` could be a build loop, debug loop, or content edit — distinguishing is on you.

## Reading

- "The Sublimate Moment" — LinkedIn Pulse, 2026-05-28.
- Post-35 on withagents.dev: longer walkthrough of the four dogfood specimens and the three-tier rubric.
- Anthropic announcement: https://claude.com/blog/introducing-dynamic-workflows-in-claude-code
- Workflows API docs: https://code.claude.com/docs/en/workflows.md

## License

MIT. © 2026 Nick Krzemienski.
