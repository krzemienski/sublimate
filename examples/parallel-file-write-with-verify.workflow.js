export const meta = {
  name: 'parallel-file-write-with-verify',
  description: 'Fan-out N writer subagents that each Write one file with exact content, then run a verify pass that reads each file and reports a metrics table (word count, placeholder count, AI-tells, citations).',
  phases: [
    { title: 'write-fan-out', detail: 'Spawn one writer subagent per target file in parallel. Each writer issues a single Write call with verbatim content and returns a short ack token.' },
    { title: 'verify-pass', detail: 'Single audit subagent reads every written file, counts words / placeholders / AI-tells / cited specimens / repo URLs, and emits a markdown table.' },
  ],
}


phase('write-fan-out')
const writeTargets = [
  { label: 'write-shared-tokens', path: '/Users/nick/Desktop/blog-series/site/src/app/sublimate/_shared.ts', ack: 'WROTE _shared' },
  { label: 'write-layout',        path: '/Users/nick/Desktop/blog-series/site/src/app/sublimate/layout.tsx',   ack: 'WROTE layout' },
  { label: 'write-page',          path: '/Users/nick/Desktop/blog-series/site/src/app/sublimate/page.tsx',     ack: 'WROTE page' },
  { label: 'write-post-md',       path: '/Users/nick/Desktop/blog-series/posts/post-35-sublimate/post.md',     ack: 'WROTE post' },
  { label: 'write-pulse',         path: '/Users/nick/Desktop/blog-series/wa/content/pulse/2026-05-28-sublimate.md',    ack: 'WROTE pulse' },
  { label: 'write-linkedin',      path: '/Users/nick/Desktop/blog-series/wa/content/linkedin/2026-05-28-sublimate.md', ack: 'WROTE linkedin' },
]

await parallel(writeTargets.map((t) => () =>
  agent(
    `Write ${t.path} via the Write tool.\n\n` +
    `The file contents are provided between BEGIN and END markers (markers themselves are NOT part of the file).\n` +
    `Issue exactly one Write call with that verbatim content — no edits, no reformatting, no added commentary.\n` +
    `When the Write tool returns success, reply with exactly: "${t.ack}".\n\n` +
    `BEGIN\n<file body inlined by caller>\nEND`,
    { label: t.label, phase: 'write-fan-out' }
  )
))


phase('verify-pass')
await agent(
  'Audit every file written in the previous phase. For each file: Read it, then run Bash word/line counts. ' +
  'Compute: word count, placeholder count (TODO / TBD / FIXME / lorem), AI-tells count (em-dash + " — ", "delve", "navigating", "in the realm of"), ' +
  'count of cited session/specimen IDs, and count of repo URLs (github.com/...).\n\n' +
  'Emit one markdown table with one row per file and the columns: File | Words | Placeholders | AI tells | Specimens cited | Repo URL.\n' +
  'If any cell would fail launch criteria (placeholders > 0, AI tells > 0, words below floor), edit the file in place to fix, then re-Read and recount.\n' +
  'Return only the final table.',
  { label: 'verify-and-fix', phase: 'verify-pass' }
)
