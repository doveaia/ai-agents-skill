---
name: newsletter
description: >
  Research competitor newsletters and generate a publication-ready draft
  in the operator's voice. The competitor list comes from the
  NEWSLETTER_SOURCES environment variable (comma-separated URLs). The
  agent fetches recent issues, identifies trending topics and coverage
  gaps, learns the operator's voice from past drafts, then writes a
  complete dated draft to disk. Use when the operator asks to
  "research the newsletter market", "draft this week's issue", or
  "find what competitors are writing about". Do NOT use for: sending the
  newsletter (delegate to the `resend` skill), one-off blog posts,
  social-media copy, or any task that needs a graphical newsletter editor.
  Do NOT use if NEWSLETTER_SOURCES is unset — stop and ask the operator
  for the source list first.
---

# Newsletter research & draft generation

This skill drives the full newsletter-writer workflow end to end:

1. Read competitor URLs from `NEWSLETTER_SOURCES`.
2. Fetch each competitor's most recent newsletter.
3. Analyse topics, trends, and coverage gaps.
4. Learn the operator's voice from past drafts.
5. Generate a complete dated draft in that voice.
6. Save the draft to disk and report back.

There is no separate CLI to invoke — the skill is a procedure the agent
runs using its standard tools (`WebFetch`, `Read`, `Glob`, `Write`).

## Prerequisites

| Variable | Required | Description |
| --- | --- | --- |
| `NEWSLETTER_SOURCES` | yes | Competitor newsletter URLs the skill fetches. **Comma-separated.** Each entry is either a bare URL or `Name <https://url>` (the human label is ignored for fetching but kept in the research notes). |
| `NEWSLETTER_VOICE_SAMPLE_COUNT` | no | How many past drafts to read for voice analysis. Defaults to `5`. Set to `0` to skip voice analysis (the draft will use a neutral newsletter tone — flag this in the report). |

The **drafts directory** (where past newsletters live AND where new
drafts are written) is supplied by the calling agent or operator — it
is not configured via an env var. If the agent did not pass a path,
ask the operator before fetching anything. Do **not** invent a default
path like `./drafts/`.

If `NEWSLETTER_SOURCES` is unset or empty, **stop immediately** and ask
the operator to export it. Do not invent URLs or fall back to a hard-coded
competitor list.

### Parsing `NEWSLETTER_SOURCES`

The variable is a single line of **comma-separated** URLs:

```bash
# Bare URLs
export NEWSLETTER_SOURCES="https://sahilbloom.com/newsletter,https://thedankoe.com/newsletter,https://www.petergyang.com/newsletter"

# Labelled (human label dropped before fetching)
export NEWSLETTER_SOURCES="Sahil Bloom <https://sahilbloom.com/newsletter>,Dan Koe <https://thedankoe.com/newsletter>"
```

Extraction rule:

1. Split on `,`.
2. Strip whitespace from each entry.
3. If an entry matches `Name <URL>`, keep `URL` for fetching and `Name`
   for the report. Otherwise the bare URL is both.
4. Drop empties and any entry that does not parse as `http(s)://…`.
5. If fewer than 2 valid URLs remain, stop and tell the operator the
   list is too short.

If the operator hands you a multi-line list (newlines instead of
commas), don't silently reinterpret — surface the format error and
ask them to re-export with commas.

## Working process

### Step 1 — Load sources

```bash
echo "$NEWSLETTER_SOURCES"
```

Parse per the rules above. Surface the parsed list back to the operator
before fetching so they can confirm. Example:

```
Parsed 6 sources from NEWSLETTER_SOURCES:
  1. Sahil Bloom — https://sahilbloom.com/newsletter
  2. Dan Koe     — https://thedankoe.com/newsletter
  ...
Fetching now.
```

### Step 2 — Fetch competitor content

For each URL, use `WebFetch` with a topic-extraction prompt — do **not**
keep the full body in context:

```
WebFetch(
  url="<competitor URL>",
  prompt="Extract: (1) the 2–4 main topics with one-sentence summaries,
          (2) the headline, (3) approximate word count, (4) the
          publication date if visible, (5) the opening style
          (story/question/observation/statement), (6) the CTA type.
          Return as a compact bulleted summary. Do NOT echo the full body."
)
```

Discard the raw HTML after extraction. Keep only the structured
summary.

If a fetch fails (404, paywall, JS-only render), note it in the report
and continue — do not retry blindly.

### Step 3 — Analyse trends (progressive disclosure)

Apply the three-level pattern:

**Level 1 — scan**: tabulate `Competitor | Date | Topics | Format | ~words`.

**Level 2 — topic frequency**: for every topic, count appearances. Bucket
into:
- **Strong trend**: ≥ 4 mentions
- **Growing**: 2–3 mentions
- **Emerging / noise**: 1 mention

**Level 3 — deep dive** (only if a strong trend exists): for the top 1–2
topics, capture the angle each competitor took and what they missed.

Identify at least one **gap** worth filling:
- Coverage gap (no one covered an obviously relevant topic)
- Depth gap (everyone stayed surface-level)
- Angle gap (everyone took the same angle)
- Practical gap (lots of theory, no how-to)
- Combination gap (two topics covered separately but never connected)

### Step 4 — Learn the voice

The calling agent must supply the **drafts directory** (where past
newsletters live). If no path was provided, ask the operator now —
do not guess.

Find the most recent N drafts (N = `NEWSLETTER_VOICE_SAMPLE_COUNT`,
default 5):

```
Glob "<drafts-dir>/newsletter-*.md"
```

Sort by filename descending (the `YYYY-MM-DD` suffix is the sort key),
take the first N, and `Read` each.

For each draft note:
- Opening style (story / question / observation / bold statement)
- Sentence rhythm (short-punchy vs flowing vs varied)
- Recurring phrases (e.g. "Here's the thing:", "Think about it:")
- Paragraph length pattern
- CTA approach (direct / soft / question / resource share)
- Closing signature
- Typical word count

Compile a short **voice profile** (≤ 15 lines) and keep it in context.
Drop the raw draft text once the profile exists.

If the drafts directory is empty (no past newsletters yet) or
`NEWSLETTER_VOICE_SAMPLE_COUNT=0`, skip this step and explicitly mark
the draft as "no voice sample available — neutral tone used" in the
report.

### Step 5 — Generate the draft

Pick 2–4 topics from the trend analysis:
- At least one strong trend (so the draft is timely)
- At least one gap-filling angle (so the draft is differentiated)

Outline → full draft. The draft is **not** an outline; produce the
actual prose at the operator's typical word count (from the voice
profile).

Required sections:

```markdown
# Newsletter — YYYY-MM-DD

## Subject line options
1. …
2. …
3. …
(3–5 total, matching the voice profile's subject pattern)

---

[Opening hook — 2–3 sentences in the operator's style]

[Body — 2–4 topic sections, each with a lead sentence, 2–4 development
paragraphs, smooth transition to the next]

[CTA — matches the operator's typical ask]

[Sign-off — operator's signature phrase]

---

## Research context

### Topics chosen
1. **<Topic>** — why (trend + angle + voice fit)
2. …

### Trends leveraged
- <Trend> — addressed in <section>

### Gap filled
- <Gap> — covered by <angle>

### Competitor coverage
- <Name>: <topic> via <angle>
- …

### Voice match notes
- <Style element>: <how implemented>
- …

### Editing suggestions
- [ ] Personal anecdote slot in <section>
- [ ] Verify data point in <section>
- [ ] Tighten transition between <A> and <B>

### Word count
- Draft: ~<n> words
- Operator's typical range: <range from voice profile>

### Failed fetches (if any)
- <URL>: <reason>
```

### Step 6 — Save the draft

Write to the same drafts directory the calling agent provided in step 4:

```
<drafts-dir>/newsletter-YYYY-MM-DD.md
```

Use today's date (`YYYY-MM-DD`). Write via the `Write` tool. If a file
already exists for today, append `-vN` (`newsletter-YYYY-MM-DD-v2.md`)
— never overwrite an existing draft.

Report:
1. Output path.
2. Number of competitors fetched / failed.
3. Top 3 trends identified.
4. The chosen gap-fill angle.
5. Whether voice analysis was used (and how many samples).
6. Draft word count.

## Quality bar before reporting "done"

- [ ] Parsed ≥ 2 valid URLs from `NEWSLETTER_SOURCES`.
- [ ] Successfully fetched ≥ half of them (otherwise warn the operator).
- [ ] Documented topic frequency (Level 2 minimum).
- [ ] Identified at least one gap with a stated angle.
- [ ] Voice profile built OR explicitly marked as skipped.
- [ ] Complete draft (not an outline) with 3–5 subject lines.
- [ ] Draft saved to the drafts directory the caller provided.
- [ ] Did not overwrite an existing same-day file.

## Anti-patterns

**Don't**:
- ❌ Hard-code competitor URLs because `NEWSLETTER_SOURCES` looks
  inconvenient — stop and ask the operator instead.
- ❌ Keep full competitor HTML in context after extraction.
- ❌ Generate an outline and call it a draft.
- ❌ Write in generic AI voice when voice samples exist.
- ❌ Copy a competitor's angle verbatim.
- ❌ Silently overwrite a same-day draft.
- ❌ Fetch every URL in parallel without summarising in between
  (context bloat).

**Do**:
- ✅ Parse the env var defensively and echo what was parsed.
- ✅ Use progressive disclosure (scan → frequency → deep dive) to keep
  context tight.
- ✅ Build a voice profile, then drop raw drafts from context.
- ✅ Differentiate from competitors using the gap analysis.
- ✅ Surface failed fetches honestly — partial coverage is fine, lying
  about coverage is not.

## Reporting back

The final message to the operator contains:

1. The parsed source list (with any rejected entries flagged).
2. Fetch outcome summary (`6/8 fetched, 2 failed: …`).
3. Top 3 trends and the chosen angle.
4. Voice match status (`5 samples used` / `no samples — neutral tone`).
5. The output file path and word count.
6. A short "next step" hint, typically:
   `Review and personalise, then ship via the resend skill.`
