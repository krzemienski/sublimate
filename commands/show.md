---
description: Show candidates from the last sublimate distill run.
---

# /sublimate:show

Read `/tmp/sublimate-run/clusters.json` and `/tmp/sublimate-run/curation.json` from the most recent distill run. Surface a review table:

| cluster_id | size | classification | top pattern | rationale |
|------------|------|----------------|-------------|-----------|

For each cluster:

- `cluster_id` — id from clusters.json
- `size` — number of member sessions
- `classification` — tier from curation.json (NOISE / SUBAGENT / SKILL / WORKFLOW) plus verdict
- `top pattern` — first entry of `top_patterns[]`
- `rationale` — one-sentence reason from curator

Also print the absolute path to each candidate artifact under `/tmp/sublimate-run/`. Suggest next step:

```
Promote with: /sublimate:promote <cluster-id>
```

If `/tmp/sublimate-run/` does not exist, tell the user to run `/sublimate:distill` first.
