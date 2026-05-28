# examples/ — what was hand-polished vs raw-emitted

## post-cover.workflow.js

Source cluster: ~14 blog-series sessions (mostly cover-regen runs across posts 21..34).
RAW emit (PrefixSpan top pattern): Read -> Bash -> Read -> Bash. Coherent shape but useless prompts ("Execute pattern: Read -> Bash").
POLISH: extracted real intent from session content — frontmatter parse + Stitch invocation + sync + 3-way parallel verify. Added FRONTMATTER_SCHEMA + CHECK_SCHEMA for structured output. Wired `args.slug` for reuse across posts.

Diff lines from raw: ~110.

## audit-verify-ship.workflow.js

Source cluster: ~23 blog-series sessions. The full-functional-audit + parallel-fix loop pattern, observed across plan dirs 260420 through 260527.
RAW emit (PrefixSpan top pattern): Glob -> Read -> Edit -> Bash -> Bash. Support 18/23.
POLISH: replaced single agent() chain with parallel() over 6 audit dimensions (a11y, metadata, links, images, rendering, performance). Used pipeline() in Fix phase so each finding fixes + verifies independently. Final Ship phase as single agent.

Diff lines from raw: ~140.

## weekly-retro.workflow.js

Source cluster: 7 sessions tied to the launchd cron at Sunday 20:11 (wa-retro.py invocations).
RAW emit (PrefixSpan top pattern): Bash -> Read -> Read -> Bash -> Write. Support 5/7.
POLISH: replaced the linear Bash/Read/Write with parallel() over 5 signal types, then a single synthesizer that reads all of them via schema-validated structured output, then a single Propose phase that emits retro.md + weight-delta.json.

Diff lines from raw: ~85.

## What this proves

The miner found the shape. The shape was right in all three cases. The MISSING piece was the prompt narrative — what each step is actually trying to do. v0.2 should LLM-distill prompts from the session content inside each pattern occurrence. Until then, examples are curator-required.

End of RATIONALE.md.
