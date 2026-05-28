# RATIONALE — what v0.1.0 actually is

This is a heuristic miner, not a magic distiller. It surfaces candidate workflows from your session history; you decide which ones are worth keeping.

## What it gets right

- Deterministic. Same input, same output. No LLM in the loop. Reproducible.
- Cheap. Runs in under a minute on 2,000+ sessions. No tokens, no API calls.
- Honest about pattern. PrefixSpan only emits subsequences that actually repeated. If your sessions never converged on a pattern, the miner will not fake one.

## What it gets wrong

- Tool-name granularity only. Two sessions that both go Read -> Edit -> Bash look similar even if one was a Python rewrite and the other was a CSS tweak. Semantic clustering is out of scope for v0.
- No agent-spawn detection. When a session spawned subagents via the Task tool, the miner sees Task calls but does not expand them. Workflows ARE about parallel agents — v0.2 should follow the spawn graph.
- Phase boundaries are heuristic. Right now phases cut at user-prompt edges. Sometimes correct (user re-orients), sometimes wrong (user just nudges).
- No prompt distillation. Emitted agent() calls have placeholder prompts like "Execute pattern: Read -> Edit -> Bash". The whole point of Workflows is rich prompts. v0.2 should LLM-distill prompts from the original session content.

## What you should do

1. Run it. workflow-distill <projects-dir> --emit-all.
2. Look at the candidates. out/cluster-N.workflow.js.
3. Pick the ones that match a process you actually run. Discard the noise.
4. Hand-polish: real agent prompts, real schema for structured output, sensible agentType hints.
5. Drop into .claude/workflows/ and /workflows it.

## Why ship it anyway

Anthropic just made Workflows a first-class primitive. The 90% of engineers who did not hand-build orchestration patterns now need a way IN. A deterministic heuristic miner is the cheapest possible v0: it cites the user's own evidence and refuses to fabricate.

If it is useful, v0.2 adds: agent-spawn following, prompt distillation, schema synthesis, cluster naming.

If it is not, you have still learned what shape your own sessions take.

## The three examples in this repo

Each is hand-polished from a real cluster on the 2,067-session blog-series corpus. The RAW emit was unusable in two cases; one was nearly-ready. See examples/RATIONALE.md for the per-example diffs.

End of RATIONALE.md.
