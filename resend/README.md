# resend

Send transactional emails, manage domains, audiences, contacts,
broadcasts, API keys, and webhooks via the official
[Resend CLI](https://resend.com/changelog/cli).

> Agent-facing instructions live in [`SKILL.md`](./SKILL.md). This file
> is the human-facing quick start.

## Prerequisites

Install the `resend` CLI on `PATH`. Pick one:

```bash
# macOS / Linux (cURL)
curl -fsSL https://resend.com/install.sh | bash

# Node 20+ (any platform)
npm install -g resend-cli

# Homebrew
brew install resend/cli/resend

# Windows (PowerShell)
irm https://resend.com/install.ps1 | iex
```

Verify:

```bash
resend --version
```

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `RESEND_API_KEY` | yes | API key from <https://resend.com/api-keys>. Must start with `re_`. |
| `RESEND_PROFILE` | no | Named profile when juggling multiple Resend teams (`resend auth switch`). |

```bash
export RESEND_API_KEY="re_…"
# Optional:
# export RESEND_PROFILE="production"
```

Persist by appending the `export` line to `~/.zshrc` or `~/.bashrc`.

You can also override per-invocation with the global `--api-key`:

```bash
resend --api-key re_other_key emails send …
```

Priority chain (highest wins): `--api-key` flag → `RESEND_API_KEY` env
var → `~/.config/resend/credentials.json` (from `resend login`).

## Usage

The skill does not ship a wrapper script — the CLI **is** the tool.
Agents and humans invoke `resend` directly. The most common entry points:

```bash
# Sanity-check environment, key, and verified domains
resend doctor --json

# Send a transactional email
resend emails send \
  --from "Sender <hello@your-verified-domain.com>" \
  --to "recipient@example.com" \
  --subject "Hello from the CLI" \
  --text "Plain-text body."

# Validate a complex send without delivering it
resend emails send … --dry-run

# List verified sending domains
resend domains list --json

# Register a webhook endpoint (HTTPS required)
resend webhooks create \
  --endpoint "https://app.example.com/hooks/resend" \
  --events email.sent email.bounced \
  --json

# Print the full command tree as JSON (great for discovery)
resend commands
```

### Output behavior

- In a TTY: human-formatted output, spinners, prompts on stderr.
- Piped, in CI, or with `--json` / `-q`: machine-readable JSON on stdout.
  Errors are JSON on stderr with `message` and `code` fields. Exit code
  `1` on any error, `0` on success.

## Safety notes

- Never log or commit your `re_…` key. The CLI masks it in `resend
  doctor` output; do the same in any tooling you build around it.
- Sends require the `--from` address to be on a **verified** domain.
  Use `resend domains list` to check.
- Webhook `signing_secret` is shown **once** at create time. Save it
  immediately; rotation requires delete + create.
- Prefer `webhooks update --status disabled` over
  `webhooks delete --yes` when reversibility matters.

## Layout

```
resend/
├── README.md              # this file
└── SKILL.md               # agent-facing instructions (paperclip)
```

## Reference

Full Resend CLI documentation:
<https://github.com/resend/resend-cli> · changelog:
<https://resend.com/changelog/cli>.
