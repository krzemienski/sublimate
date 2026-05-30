---
name: audit-e2e
description: E2E user-journey audit worker for live web app. Per-journey browser session via chrome-devtools MCP — open page, screenshot + DOM snapshot, click via uid refs, capture evidence into per-journey dirs, emit PASS/FAIL report.
allowed-tools: mcp__chrome-devtools__list_pages, mcp__chrome-devtools__new_page, mcp__chrome-devtools__select_page, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__click, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__close_page, Bash, Write, TaskCreate, TaskUpdate
---

# audit-e2e

Worker skill for team-orchestrated E2E user-journey validation on live production web app. One browser tab per journey, KISS protocol: navigate → snapshot → click via uid → verify → screenshot → close.

## Iron Rule (inherited)

No mocks. No test files. Validate against the running production system through the same surfaces a real user touches. Every PASS/FAIL cites a screenshot file path.

## Inputs

Caller (team lead) supplies:
- **Journey list** — `J1..JN`: each = start URL + ordered click steps + terminal assertion (URL pattern, DOM text, HTTP status).
- **Evidence root** — absolute path, e.g. `evidence/<trial>/audit-e2e/`.
- **Mandatory skill receipts** — invoke `e2e-validate`, `agent-browser`, `functional-validation` first, cite their `SKILL.md` paths in final report.

## Procedure

### 0. Bootstrap

```bash
mkdir -p <evidence-root>/{J1,J2,...,JN}
```

Invoke mandatory skills in single batch (one tool block, parallel) to record receipts.

### 1. Browser session check

`mcp__chrome-devtools__list_pages` — confirm browser alive. Note currently-selected `pageId`.

Pitfall: `new_page` does NOT auto-select. After `new_page` the new tab gets a fresh id; old selection persists. Always re-`list_pages` after `new_page` and `select_page` to the new id before snapshotting — otherwise `take_snapshot` returns `about:blank`.

### 2. Per-journey loop

For each `J{n}` (serial — chrome-devtools session is single-tab-focused):

1. **Open** — `mcp__chrome-devtools__new_page` url=<journey start>.
2. **Re-list + select** — `list_pages` → identify new tab id → `select_page` pageId=<new>. Confirm selected URL matches start URL.
3. **Initial capture** — `take_screenshot` filePath=`<evidence-root>/J{n}/01-<slug>.png`.
4. **Snapshot DOM** — `take_snapshot`. Output gives uid refs (`uid=N_M`) for every interactive element. Find target by visible text / role.
5. **Click + verify** — `mcp__chrome-devtools__click` uid=<ref>. Then `take_screenshot` → `02-<next-slug>.png`. Re-`take_snapshot` if next step needs a uid.
6. **Assertion step** — for terminal step use `evaluate_script` to confirm URL / DOM text / HTTP status. For external nav (e.g. GitHub) accept new tab; verify URL via `list_pages`.
7. **Close** — `mcp__chrome-devtools__close_page` pageId=<journey tab>. Prevents tab accumulation breaking subsequent journeys.

Number screenshots `NN-<slug>.png` zero-padded so file sort = step order.

### 3. Common journey shapes

| Shape | Steps |
|-------|-------|
| Card → detail → outbound | home → click card uid → detail page screenshot → click outbound link uid → external URL screenshot |
| Catalog → product → subdomain | `/products` → click product mini-card uid → `/products/<slug>` → click "View product site" → `<slug>.withagents.dev` |
| Prev/next nav | `/posts/<n>` → assert sidebar shows prev+next → click next uid → `/posts/<n+1>` |
| Deep link | section root → click nav item uid → child route renders |
| 404 → recovery | nonexistent URL → 404 page → click home link → `/` |

### 4. FAIL handling

If a step fails (404 unexpected, click missed, assertion false):
- Capture failure screenshot `XX-FAIL-<symptom>.png`.
- Capture failing DOM via `take_snapshot` → save to `XX-FAIL.snapshot.txt` via Bash heredoc.
- Record suspected root cause in journey verdict (broken link href / missing element uid / wrong route).
- Continue to next journey — do NOT abort whole run.

### 5. Report

Write `<evidence-root>/REPORT.md`:

```markdown
# audit-e2e — trial <id>

## Skill receipts
- e2e-validate: /Users/nick/.claude/skills/e2e-validate/SKILL.md
- agent-browser: <repo>/.claude/skills/agent-browser/SKILL.md
- functional-validation: /Users/nick/.claude/skills/functional-validation/SKILL.md

## J1: <name> — PASS|FAIL
- Step 1 ✅ <evidence-root>/J1/01-home.png — homepage rendered
- Step 2 ✅ <evidence-root>/J1/02-post.png — post body + sidebar visible
- Step 3 ✅ <evidence-root>/J1/03-github.png — repo URL <url>
- Verdict: PASS

## J2: ... 
...

## Summary
N/N PASS · M FAIL · root causes: ...
```

Mark TaskCreate task `completed` via TaskUpdate. DM team-lead with one-line summary + REPORT.md path.

## Anti-patterns

- Snapshotting before `select_page` to new tab → returns `about:blank` (wasted screenshot).
- Skipping `close_page` → tab list grows, subsequent `select_page` by stale id errors `No page found`.
- Writing PASS without screenshot citation → violates evidence rule.
- Spawning multiple parallel `new_page` calls → chrome-devtools MCP serializes them; no speedup, just race on selected-tab.
- Creating test files / mocks to simulate journey → Iron Rule violation, instant FAIL of run.
