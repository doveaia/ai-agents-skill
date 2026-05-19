---
name: resend
description: >
  Send transactional emails, manage domains, audiences, contacts,
  broadcasts, API keys, and webhooks via the official Resend CLI
  (`resend`). Use when the agent needs to send an email, verify a sending
  domain, register a webhook endpoint, schedule a broadcast, or otherwise
  interact with the Resend platform from a shell. Do NOT use for: SMTP
  servers other than Resend, inbound email parsing without a Resend
  inbox, or anything requiring a graphical Resend dashboard. Do NOT use
  if `resend` is not on PATH or if RESEND_API_KEY is not set — install
  the CLI and request the key from the operator first.
---

# Resend CLI

This skill teaches agents how to drive the official Resend CLI (`resend`)
non-interactively. The CLI is the source of truth — there is no Python
wrapper here. The agent invokes `resend ...` as a subprocess and parses
the JSON it prints on stdout.

## Prerequisites

1. `resend` available on `PATH` (`resend --version` returns a version).
   Install via:

   ```bash
   curl -fsSL https://resend.com/install.sh | bash   # macOS / Linux
   npm install -g resend-cli                         # any Node 20+ env
   brew install resend/cli/resend                    # Homebrew
   ```

2. The environment variable `RESEND_API_KEY` exported with a valid
   Resend API key (starts with `re_`). If it is missing, stop and ask
   the operator — **never hard-code keys**. The CLI also accepts
   `--api-key re_...` as the highest-priority override.

3. (Optional) `RESEND_PROFILE` if the operator manages multiple Resend
   teams via `resend auth switch`.

## Logging in non-interactively

Before running any other Resend command, the agent must ensure the CLI
is authenticated. The credentials file `~/.config/resend/credentials.json`
is what `resend login` writes — without it (or without `RESEND_API_KEY`
in the env), every call returns `auth_error`.

Check the connection first:

```bash
resend doctor --json
```

If the `API Key` check is **not** `pass` (or you see `auth_error` from
any command), log in non-interactively using the key — **do not** open
the browser flow, that requires a TTY:

```bash
resend login --key "$RESEND_API_KEY"
```

Rules:

- Always pass the key via `--key`. The bare `resend login` opens a
  browser and blocks on user input, which fails in agent contexts.
- Never echo or log the key value. Pass it through the env var
  (`"$RESEND_API_KEY"`); do not interpolate the literal `re_...` string
  into shell history or transcripts.
- If `RESEND_API_KEY` itself is unset, stop and ask the operator —
  there is nothing to log in with.
- After `resend login --key`, re-run `resend doctor --json` to confirm
  `API Key: pass` before proceeding.

## How the CLI behaves with agents

- Stdout is **success JSON only** when stdout is not a TTY (pipes, CI,
  agent subprocesses). Errors go to **stderr** as JSON with `message`
  and `code` fields. Capture both: `resend ... 2>err.json >out.json`.
- Exit code: `0` success, `1` any error.
- Force JSON in any context with the global `--json` flag.
- Suppress all status output with `-q` / `--quiet` (implies `--json`).
- Discover the full command tree programmatically: `resend commands`.

Before any first email send, **always run** `resend doctor --json` and
verify:
- `API Key` check is `pass` — if not, run `resend login --key "$RESEND_API_KEY"`
  (see "Logging in non-interactively" above) and re-check.
- `Domains` check shows at least one verified domain whose name matches
  the `--from` address you intend to use

## Sending an email (primary use case)

```bash
resend emails send \
  --from "Sender Name <hello@your-verified-domain.com>" \
  --to "recipient@example.com" \
  --subject "Hello from the CLI" \
  --text "Plain-text body."
```

### Required flags

- `--from <addr>` — sender on a verified domain (see "Verifying domains").
- `--to <addr...>` — one or more recipients, space-separated.
- `--subject <subject>`
- Exactly one body source: `--text`, `--html`, or `--html-file <path>`.

### Optional flags

- `--cc <addr...>`, `--bcc <addr...>`, `--reply-to <addr>`
- Append `--dry-run` to validate the payload **without sending**. The
  CLI prints `{ "dryRun": true, "request": { ... } }`. Use this on any
  send that is high-impact, large, or templated from user input.

### Success / error output

Success:

```json
{ "id": "49a3999c-0ce1-4ea6-ab68-afcd6dc2e794" }
```

Error codes worth handling explicitly:

| `code` | Meaning | Agent action |
| --- | --- | --- |
| `auth_error` | No API key found / invalid | Stop, ask operator for `RESEND_API_KEY`. |
| `missing_body` | None of `--text`/`--html`/`--html-file` set | Add a body and retry. |
| `file_read_error` | `--html-file` path unreadable | Verify path; do not retry blindly. |
| `send_error` | Resend API rejected the send | Read `message`; common causes: unverified `from`, invalid recipient, rate limit. |

### HTML emails

For anything beyond a one-line text body, write the HTML to a file and
pass `--html-file`:

```bash
resend emails send \
  --from "you@your-domain.com" \
  --to "subscriber@example.com" \
  --subject "Newsletter — May edition" \
  --html-file ./newsletter.html
```

Always inline CSS for compatibility; the CLI does not transform HTML.

## Verifying domains before sending

```bash
resend domains list --json
```

Look for entries with `"status": "verified"`. If none match the `--from`
domain you need, the operator must add and verify a domain in the Resend
dashboard or via `resend domains create --name <domain>` followed by
publishing the returned DNS records. **Do not attempt to send from
sandbox addresses like `onboarding@resend.dev` for production traffic.**

## Webhooks

| Goal | Command |
| --- | --- |
| List existing endpoints | `resend webhooks list --json` |
| Register a new endpoint | `resend webhooks create --endpoint https://… --events email.sent email.bounced --json` |
| Subscribe to every event | `resend webhooks create --endpoint https://… --events all --json` |
| Disable temporarily | `resend webhooks update <id> --status disabled --json` |
| Delete permanently (non-interactive) | `resend webhooks delete <id> --yes --json` |

The `signing_secret` returned by `webhooks create` is shown **once** —
the agent must hand it back to the operator immediately for storage.
There is no way to recover it later; rotation requires delete + create.

Endpoint URLs **must be HTTPS**.

Event categories: `email.*` (sent, delivered, bounced, complained,
opened, clicked, failed, scheduled, suppressed, delivery_delayed,
received), `contact.*` (created, updated, deleted), `domain.*` (created,
updated, deleted). Pass `all` to subscribe to everything.

## Broadcasts (bulk)

Broadcasts target an audience and accept natural-language scheduling
(`"in 1 hour"`, `"tomorrow morning"`) or ISO 8601 timestamps. Always
preview with `--dry-run` before scheduling/sending to large audiences.

```bash
resend broadcasts create \
  --audience-id aud_xxx \
  --from "you@your-domain.com" \
  --subject "May newsletter" \
  --html-file ./newsletter.html \
  --dry-run
```

## Discovery

Print the complete CLI command tree as JSON (subcommands, flags,
descriptions). Useful when the agent needs to construct a command this
SKILL.md does not cover:

```bash
resend commands
```

## Safety rules for agents

1. **Never** log, echo, or commit `RESEND_API_KEY` or any `re_...` value.
2. **Confirm the verified `--from` domain** with `resend domains list`
   before the first send of any workflow.
3. **Use `--dry-run`** for `emails send` and `broadcasts create` whenever
   the recipient list or body is large, dynamic, or user-generated.
4. For destructive operations (`webhooks delete`, future deletes) in
   non-interactive mode you must pass `--yes`. Prefer
   `update --status disabled` over `delete` when reversibility matters.
5. If `resend doctor --json` reports any `fail`, stop and surface the
   message verbatim to the operator before attempting the requested
   action.

## Reporting back

After any send or mutation, the agent should report:

1. The command run (with the API key redacted to `re_***`).
2. The success JSON (e.g. `{"id":"..."}`) or the error JSON.
3. For sends: from, to, subject, and whether `--dry-run` was used.
4. For webhook creates: the new `id` and a reminder that the
   `signing_secret` has been disclosed and must be stored now.
