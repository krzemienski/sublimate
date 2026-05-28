# sublimate

> Distill your Claude Code session history into reusable Workflow scripts. Pattern-mining for agentic engineers.

Status: v0.1.0 — research preview, paired with Anthropic's Dynamic Workflows release at https://claude.com/blog/introducing-dynamic-workflows-in-claude-code (2026-05-28).

## What it does

Walks JSONL session files in your Claude Code projects directory. Clusters sessions by tool-call similarity (k=3 shingles + Jaccard). Mines frequent subsequences (PrefixSpan) and emits one `.workflow.js` per cluster you can drop into `.claude/workflows/`.

## Why

What serious agent-builders developed by hand for six months — phase boundaries, parallel sub-agent fan-out, scoped tool grants, deterministic checkpoints — is now a Claude Code primitive. The patterns are already sitting in your own session history, waiting to be distilled. This tool reads what you actually did, finds the repeats, and emits scaffolds you can curate into real Workflows. Background: [Anthropic announcement](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code), [Workflows API docs](https://code.claude.com/docs/en/workflows.md).

## Quickstart

```bash
pip install -e .
workflow-distill ~/.claude/projects/-Users-nick-Desktop-myproject --out ./out --emit-all
ls out/
```

Then drop a candidate into `.claude/workflows/` and run `/workflows`.

## Install

```bash
git clone https://github.com/krzemienski/sublimate
cd sublimate
pip install -e .
```

Python >= 3.10. Single runtime dep: `jinja2`.

## How it works

1. Parser walks `.jsonl` files, extracts `(role, tool_name, tool_input_hash)` per turn.
2. Shingle: `k=3` tool n-grams as sets per session.
3. Cluster: union-find on Jaccard >= 0.35.
4. PrefixSpan: top frequent subsequences per cluster (min support 0.4).
5. Emitter: Jinja to `.workflow.js` with literal `meta` block, `phase()`/`agent()`/`parallel()` body.

## Examples

Three real workflows distilled from 2,067 blog-series sessions:

- `examples/post-cover.workflow.js` — generate Stitch cover, sync to site, parallel verify.
- `examples/audit-verify-ship.workflow.js` — parallel audit, fix waves, visual verify, deploy.
- `examples/weekly-retro.workflow.js` — mine 7d, aggregate, propose weight deltas, emit `retro.md`.

See `examples/RATIONALE.md` for what was hand-polished vs raw-emitted.

## Caveats (v0.1.0)

- Heuristic, not ML. The algorithm proposes; you curate.
- Dynamic Workflows requires Claude Code v2.1.154+ on Pro / Max / Team / Enterprise. The CLI miner runs anywhere; emitted scripts need that runtime.
- Tool-call patterns are not semantic intent. `Read -> Edit -> Bash` could be a build loop, debug loop, or content edit — distinguishing is on you.

## Reading

- "The Workflow Moment" — LinkedIn Pulse, 2026-05-28.
- Post-35 on withagents.dev: longer walkthrough with three BEFORE/AFTER examples.
- Anthropic announcement: https://claude.com/blog/introducing-dynamic-workflows-in-claude-code
- Workflows API docs: https://code.claude.com/docs/en/workflows.md

## License

MIT. © 2026 Nick Krzemienski.
