---
description: Distill repeatable Workflow scripts from your Claude Code session history.
---

# /sublimate:distill

Invoke the `sublimate-distiller` skill on the current project's session corpus.

If `$ARGUMENTS` contains `--project-dir <path>`, pass it through to the skill. Otherwise default to `~/.claude/projects/$(basename "$PWD" | sed 's|/|-|g; s|^|-|')` — Claude Code's encoded directory for the current project.

Use the Skill tool:

```
Skill(skill: "sublimate-distiller", args: "$ARGUMENTS")
```

The skill walks the corpus, clusters sessions, classifies each cluster by tier, dispatches per-cluster prompt distillation, and emits candidates under `/tmp/sublimate-run/`. Review candidates with `/sublimate:show` and promote with `/sublimate:promote <cluster-id>`.
