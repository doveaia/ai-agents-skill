# newsletter

Research competitor newsletters and generate publication-ready drafts in
the operator's voice. The competitor list is supplied via the
`NEWSLETTER_SOURCES` environment variable — no on-disk links file
required.

> Agent-facing instructions live in [`SKILL.md`](./SKILL.md). This file
> is the human-facing quick start.

Adapted from the Claude Code
[`newsletter`](https://github.com/yourusername/claude-code-plugins/tree/main/plugins/newsletter)
plugin (`content-researcher` + `newsletter-writer` agents) into a single
Paperclip skill.

## Prerequisites

No external CLI to install — the skill uses the agent's built-in
`WebFetch`, `Read`, `Glob`, and `Write` tools.

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `NEWSLETTER_SOURCES` | yes | Competitor newsletter URLs, **comma-separated**. Optional `Name <https://url>` syntax is supported (label is kept for the report, URL is used for fetching). |
| `NEWSLETTER_VOICE_SAMPLE_COUNT` | no | Past drafts to read for voice cloning. Defaults to `5`. `0` disables voice analysis. |

The **drafts directory** (where past newsletters live and where new
drafts are written) is supplied by the calling agent or operator at
invocation time — not via an env var.

```bash
# Minimum config — comma-separated URLs
export NEWSLETTER_SOURCES="https://sahilbloom.com/newsletter,https://thedankoe.com/newsletter,https://www.petergyang.com/newsletter,https://www.alexandruburlacu.com/newsletter,https://every.to"

# Optional
export NEWSLETTER_VOICE_SAMPLE_COUNT=5
```

Persist by appending the `export` lines to `~/.zshrc` or `~/.bashrc`.

## Usage

Ask the agent something like:

> "Run the newsletter skill and draft this week's issue.
>  Drafts live in `~/venavi/newsletter/drafts`."

The agent will:

1. Parse `NEWSLETTER_SOURCES` and echo back the list it understood.
2. Fetch each competitor's most recent newsletter and extract topics.
3. Identify trending topics, coverage gaps, and a differentiated angle.
4. Read up to `NEWSLETTER_VOICE_SAMPLE_COUNT` past drafts from the
   drafts directory you provided to learn the voice.
5. Generate a complete draft (subject lines + body + CTA + sign-off).
6. Write it to `<drafts-dir>/newsletter-YYYY-MM-DD.md`.

If `NEWSLETTER_SOURCES` is unset, or the drafts directory was not
provided, the agent stops and asks rather than guessing.

## Output

```
<drafts-dir>/
└── newsletter-2026-05-19.md
```

The draft file contains:

- 3–5 subject-line options matching the operator's voice.
- A full body (not an outline) at the operator's typical word count.
- A research-context block listing the trends leveraged, the gap filled,
  competitor coverage, voice-match notes, and editing suggestions.

Same-day re-runs produce `newsletter-YYYY-MM-DD-v2.md`, etc.;
existing drafts are never overwritten.

## Pairing with other skills

- [`resend`](../resend/) — ship the finalised draft as a broadcast.
- [`googlecli`](../googlecli/) — pull research links from a Google Sheet
  or Docs file into `NEWSLETTER_SOURCES`.

## Layout

```
newsletter/
├── README.md              # this file
└── SKILL.md               # agent-facing instructions (paperclip)
```

## Reference

Paperclip skill format: <https://docs.paperclip.ing/#/guides/org/skills/skills>.
