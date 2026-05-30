---
name: dream-memory-consolidation
description: Reflective pass over project memory directory — orient on existing memories, gather new signal from logs/transcripts, consolidate into topic files, prune the MEMORY.md index. Use when invoking /dream or when user asks to "consolidate memory", "compact memories", "update MEMORY.md", or when memory index has drifted from codebase reality.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Dream — Memory Consolidation

Synthesize recent learning into durable, well-organized project memories so future sessions orient quickly. Memory directory is the source of truth; `MEMORY.md` is index, topic files are content.

## Inputs

- **Memory dir:** `/Users/nick/.claude/projects/<project-slug>/memory/` (already exists — never `mkdir`)
- **Session transcripts:** `/Users/nick/.claude/projects/<project-slug>/*.jsonl` (large — grep narrowly, never read whole files)
- **Codebase:** current working directory

## Phase 1 — Orient

1. `ls -la <memory-dir>` — see existing topic files + lock files
2. Read `MEMORY.md` fully — understand current index shape, what topics exist
3. Skim 2-4 existing topic files most likely to drift (recent project-state, architecture, feedback). Goal: update in place, do not duplicate
4. Check `logs/` and `sessions/` subdirs if present (assistant-mode layout); skip cleanly if absent

## Phase 2 — Gather recent signal

Priority order:

1. **Daily logs** `logs/YYYY/MM/YYYY-MM-DD.md` if present — append-only stream of recent observations
2. **Drift detection** — compare memory claims against current codebase (file paths, counts, frontmatter fields, framework versions). Any contradiction = repair target
3. **Codebase probes** — `ls posts/`, `cat package.json`, `git log --oneline -20`, frontmatter greps. Cheap reality-checks beat transcript spelunking
4. **Narrow transcript grep** — only when you already suspect a specific fact matters:
   ```
   grep -rn "<narrow term>" <project-jsonl-dir> --include="*.jsonl" | tail -50
   ```
   Never exhaustively read transcripts.

## Phase 3 — Consolidate

For each fact worth keeping, write or update a topic file at the top level of memory dir. Naming convention from existing files: `project_<topic>.md`, `feedback_<lesson>.md`, `<feature>_<context>.md` (kebab snake mix — match what is already there).

Rules:

- **Merge, do not duplicate** — if a topic file already covers it, edit rather than create a near-duplicate
- **Absolute dates only** — convert "yesterday" / "last week" / "recently" to `YYYY-MM-DD`. Memories outlive the relative frame
- **Delete contradicted facts at source** — if today's investigation disproves an old claim, fix the topic file, not just the index
- **One topic per file** — do not bundle unrelated lessons; split if a file grows beyond one coherent subject
- **Cite paths** — concrete `path:line` or filename when claiming code state

What NOT to save:

- Ephemeral build output, one-off bug repro logs, exact error strings without context
- Session-specific scratch (which agent ran when, intermediate tool outputs)
- Anything already encoded as a project rule or canonical doc

## Phase 4 — Prune and index

Open `MEMORY.md`. Rebuild it as a thin index:

- **Hard caps:** under 200 lines AND under ~25KB
- **Line format:** `- [Title](file.md) — one-line hook under ~150 chars`
- **Never** embed memory content directly in `MEMORY.md` — that belongs in topic files
- **Demote bloat** — any index line over ~200 chars is carrying content; shorten the line, move the detail to the topic file
- **Remove stale pointers** — entries whose topic file was deleted, superseded, or contradicted
- **Add new pointers** — for topic files created/updated in Phase 3
- **Resolve contradictions** — if two topic files disagree, fix the wrong one (do not leave both pointers)

Keep section headers stable (Project State, Posts, Key Paths, Architecture, Feedback / Lessons, Pipeline Lessons, Design System, etc.). New sections only when a genuinely new topic cluster emerges.

## Output

Brief summary listing:

- Topic files created / updated / deleted (paths)
- `MEMORY.md` index lines added / removed / demoted
- Drift repairs applied (old claim → new claim with date)
- If nothing changed, say so explicitly

## Anti-patterns

- Creating new topic files when an existing one covers the subject
- Writing memory content into `MEMORY.md` instead of a topic file
- Leaving relative dates ("yesterday") in saved memories
- Exhaustive transcript reads instead of narrow greps
- `mkdir` on the memory directory (it always exists)
- Treating memory as live state — every read is a point-in-time observation, verify against code before asserting
