export const meta = {
  name: 'weekly-retro',
  description: 'Mine 7 days of sessions in parallel, aggregate via synthesizer, propose weight deltas',
  phases: [
    { title: 'Mine',      detail: 'Parallel mine of 5 signal types over the last 7 days' },
    { title: 'Aggregate', detail: 'Single synthesizer reads all 5 outputs (schema-validated)' },
    { title: 'Propose',   detail: 'Emit retro.md + weight-delta.json proposal' },
  ],
}

const SIGNAL_TYPES = [
  { key: 'mine',     prompt: 'Walk ~/.claude/projects/ for sessions touched in the last 7 days. Extract topic keywords from user prompts. Output: { topics: [{topic: string, count: int, sessions: string[]}] }.' },
  { key: 'triage',   prompt: 'Walk session logs for triage decisions (DEFER, BLOCK, RESOLVE) in the last 7 days. Output: { decisions: [{kind: string, count: int, contexts: string[]}] }.' },
  { key: 'stages',   prompt: 'Walk plan dirs touched in the last 7 days; extract phase status transitions. Output: { phases: [{plan: string, phase: string, status: string}] }.' },
  { key: 'cadence',  prompt: 'Walk wa-cadence-fire logs for the last 7 days; extract publish events + click-through metrics. Output: { posts: [{url: string, impressions: int, clicks: int}] }.' },
  { key: 'archived', prompt: 'Walk .archive/ for items archived in the last 7 days. Output: { archives: [{path: string, reason: string, date: string}] }.' },
]

const SIGNAL_SCHEMA = {
  type: 'object',
  properties: {
    topics:    { type: 'array' },
    decisions: { type: 'array' },
    phases:    { type: 'array' },
    posts:     { type: 'array' },
    archives:  { type: 'array' },
  },
}

const WEIGHT_DELTA_SCHEMA = {
  type: 'object',
  required: ['proposals'],
  properties: {
    proposals: {
      type: 'array',
      items: {
        type: 'object',
        required: ['dimension', 'current', 'proposed', 'rationale'],
        properties: {
          dimension: { type: 'string' },
          current:   { type: 'number' },
          proposed:  { type: 'number' },
          rationale: { type: 'string' },
        },
      },
    },
  },
}

phase('Mine')
const signals = await parallel(
  SIGNAL_TYPES.map(s => () => agent(s.prompt, { schema: SIGNAL_SCHEMA, label: `mine:${s.key}`, phase: 'Mine' }))
)

phase('Aggregate')
const aggregated = await agent(
  `You are the weekly retro synthesizer. Read these five signal outputs:

${signals.map((s, i) => `Signal ${SIGNAL_TYPES[i].key}: ${JSON.stringify(s)}`).join('\n\n')}

Identify the 3-5 highest-leverage themes. For each, propose a weight delta (-0.2 to +0.2) on the relevant attention dimension. Output schema-validated proposal list.`,
  { schema: WEIGHT_DELTA_SCHEMA, label: 'synthesize', phase: 'Aggregate' }
)

phase('Propose')
const retro = await agent(
  `Compose retro.md for the week ending today (use the date passed in args.weekEnd). Sections: Themes, Wins, Drift, Proposed Weight Deltas (table from ${JSON.stringify(aggregated.proposals)}). Save to wa/retro/${args?.weekEnd ?? 'YYYY-MM-DD'}-retro.md. Report the path.`,
  { label: 'compose-retro', phase: 'Propose' }
)

return { signals: signals.length, themes: aggregated.proposals.length, retro }
