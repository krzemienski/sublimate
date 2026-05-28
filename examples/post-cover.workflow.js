export const meta = {
  name: 'post-cover',
  description: 'Generate Stitch cover for a post, sync to site, run parallel verifies',
  phases: [
    { title: 'Parse',    detail: 'Read post frontmatter' },
    { title: 'Generate', detail: 'Invoke Stitch with prompt block from DESIGN.md §6' },
    { title: 'Sync',     detail: 'Copy rendered cover to site/public/linkedin-assets/' },
    { title: 'Verify',   detail: 'Parallel dimension + color-space + alt-text checks' },
  ],
}

const POST_SLUG = args?.slug ?? 'post-XX-untitled'

const FRONTMATTER_SCHEMA = {
  type: 'object',
  required: ['title', 'subtitle', 'series_number'],
  properties: {
    title:        { type: 'string' },
    subtitle:     { type: 'string' },
    series_number:{ type: 'string' },
    tags:         { type: 'array', items: { type: 'string' } },
  },
}

const CHECK_SCHEMA = {
  type: 'object',
  required: ['pass', 'evidence'],
  properties: {
    pass:     { type: 'boolean' },
    evidence: { type: 'string' },
    note:     { type: 'string' },
  },
}

phase('Parse')
const fm = await agent(
  `Read posts/${POST_SLUG}/post.md, parse YAML frontmatter, return as structured output.`,
  { schema: FRONTMATTER_SCHEMA, label: 'read-frontmatter' }
)

phase('Generate')
const cover = await agent(
  `Generate a Stitch cover image. Title: ${fm.title}. Subtitle: ${fm.subtitle}. Use the prompt block from DESIGN.md Section 6 (Stitch prompts). Save to posts/${POST_SLUG}/assets/linkedin-hero-01-cover.png. Report the absolute path.`,
  { label: 'stitch-render' }
)

phase('Sync')
await agent(
  `Copy ${cover} to site/public/linkedin-assets/${POST_SLUG}/linkedin-hero-01-cover.png. Use cp via Bash. Verify copy succeeded.`,
  { label: 'sync-to-site' }
)

phase('Verify')
const verdicts = await parallel([
  () => agent(
    `Open the cover at site/public/linkedin-assets/${POST_SLUG}/linkedin-hero-01-cover.png and verify dimensions are 1200x627 (LinkedIn hero spec). Report pass: true if exact match.`,
    { schema: CHECK_SCHEMA, label: 'verify-dims' }
  ),
  () => agent(
    `Verify the cover at site/public/linkedin-assets/${POST_SLUG}/linkedin-hero-01-cover.png is sRGB color space (LinkedIn requires sRGB). Use imagemagick identify -format '%[colorspace]'. Report pass: true if "sRGB".`,
    { schema: CHECK_SCHEMA, label: 'verify-colorspace' }
  ),
  () => agent(
    `Compose alt-text from frontmatter title and subtitle: "${fm.title} — ${fm.subtitle}". Report pass: true and evidence: the alt-text string.`,
    { schema: CHECK_SCHEMA, label: 'verify-alttext' }
  ),
])

const allPass = verdicts.every(v => v && v.pass)
log(`post-cover ${allPass ? 'PASS' : 'FAIL'} for ${POST_SLUG}`)
return { post: POST_SLUG, cover, pass: allPass, verdicts }
