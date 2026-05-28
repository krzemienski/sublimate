export const meta = {
  name: 'audit-verify-ship',
  description: 'Parallel multi-perspective audit, pipeline fix loop, visual verify, deploy',
  phases: [
    { title: 'Find',   detail: 'Parallel scouts over 6 audit perspectives' },
    { title: 'Fix',    detail: 'Pipeline each finding through fix + per-item adversarial re-audit' },
    { title: 'Verify', detail: 'Visual + functional regression check on changed routes' },
    { title: 'Ship',   detail: 'Submodule bump, commit, vercel deploy --prod, HTTP 200 verify' },
  ],
}

const DIMENSIONS = [
  { key: 'a11y',        prompt: 'Audit live site for WCAG 2.1 AA violations. Use chrome-devtools MCP. Report findings as structured list.' },
  { key: 'metadata',    prompt: 'Audit OG meta, Twitter cards, JSON-LD across changed routes. Report missing or malformed.' },
  { key: 'links',       prompt: 'Audit cross-post links + outbound links for 4xx/5xx. Use HEAD requests via curl.' },
  { key: 'images',      prompt: 'Audit images for missing alt-text, wrong aspect ratio, broken SVG embeds.' },
  { key: 'rendering',   prompt: 'Audit rendered output for visual regressions vs baseline screenshots.' },
  { key: 'performance', prompt: 'Audit Lighthouse performance for changed routes. Flag any drop below 90.' },
]

const FINDINGS = {
  type: 'object',
  required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'route', 'severity', 'description'],
        properties: {
          id:          { type: 'string' },
          route:       { type: 'string' },
          severity:    { enum: ['critical', 'major', 'minor'] },
          description: { type: 'string' },
        },
      },
    },
  },
}

const VERDICT = {
  type: 'object',
  required: ['fixed', 'evidence'],
  properties: {
    fixed:    { type: 'boolean' },
    evidence: { type: 'string' },
    note:     { type: 'string' },
  },
}

phase('Find')
const auditResults = await parallel(
  DIMENSIONS.map(d => () => agent(d.prompt, { schema: FINDINGS, label: `audit:${d.key}`, phase: 'Find' }))
)

const allFindings = auditResults
  .filter(Boolean)
  .flatMap(r => r.findings)
  .filter(f => f.severity !== 'minor')

log(`Find phase complete: ${allFindings.length} non-minor findings across ${DIMENSIONS.length} dimensions`)

phase('Fix')
const fixed = await pipeline(
  allFindings,
  (f) => agent(
    `Fix finding ${f.id} on route ${f.route}: ${f.description}. Apply the minimal change. Run pnpm build to verify no regression. Report fixed: true if build passes.`,
    { schema: VERDICT, label: `fix:${f.id}`, phase: 'Fix' }
  ),
  (verdict, originalFinding) => agent(
    `Adversarially verify the fix for ${originalFinding.id}: ${verdict.evidence}. Re-run the original audit check on ${originalFinding.route}. Report fixed: true ONLY if defect is gone AND no new regression introduced.`,
    { schema: VERDICT, label: `re-audit:${originalFinding.id}`, phase: 'Fix' }
  ),
)

const confirmedFixes = fixed.filter(Boolean).filter(v => v.fixed)
log(`Fix phase complete: ${confirmedFixes.length}/${allFindings.length} confirmed fixed`)

phase('Verify')
const visualVerdict = await agent(
  'Take browser screenshots of every route changed by the fix wave. Compare against pre-fix baseline. Report any visual regression with route + screenshot path.',
  { label: 'visual-verify', phase: 'Verify' }
)

phase('Ship')
const deployVerdict = await agent(
  'Commit blog-series changes with conventional commit. Bump site/ submodule pointer. Run vercel deploy --prod from site/. Capture deploy URL. Verify HTTP 200 on three changed routes. Report deploy URL + verdict.',
  { label: 'ship', phase: 'Ship' }
)

return { findings: allFindings.length, fixed: confirmedFixes.length, visual: visualVerdict, deploy: deployVerdict }
