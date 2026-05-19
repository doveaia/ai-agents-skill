# googlecli

Drive Google Workspace (Gmail, Calendar, Drive, Docs, Sheets, Slides,
Contacts, Tasks, Admin, …) from the terminal via the official
[`gog` CLI](https://gogcli.sh).

> Agent-facing instructions live in [`SKILL.md`](./SKILL.md). This file
> is the human-facing quick start.

## Prerequisites

Install the `gog` CLI on `PATH`. Pick one:

```bash
# macOS / Linux (Homebrew)
brew install gogcli

# Docker (any platform)
docker run --rm ghcr.io/openclaw/gogcli:latest version

# Windows (PowerShell): download the matching zip and add gog.exe to PATH
# https://github.com/openclaw/gogcli/releases

# From source (any platform with Go + make)
git clone https://github.com/openclaw/gogcli.git
cd gogcli && make
```

Verify:

```bash
gog --version
```

## One-time OAuth setup

`gog` talks to Google via your own OAuth client — there is no shared
key. Create a **Desktop app** OAuth client in Google Cloud Console,
download `client_secret_*.json`, then:

```bash
# 1. Register the OAuth client with gog (once per machine)
gog auth credentials ~/Downloads/client_secret_*.json

# 2. Authorize an account with the scopes you need
gog auth add you@gmail.com \
  --services gmail,calendar,drive,docs,sheets,contacts

# 3. Verify
gog auth list --check
gog auth doctor --check
```

Headless flow: add `--manual` (paste the consent code back) or split
across two machines with `--remote --step 1` / `--step 2`.

> Refresh tokens from an OAuth app in **External / Testing** expire
> after 7 days. Publish the app for production agents.

### Default account

Save typing `--account` everywhere:

```bash
export GOG_ACCOUNT=you@gmail.com
gog auth alias set default you@gmail.com
```

### Headless keyring (CI / Docker)

When no Keychain / Secret Service is available:

```bash
export GOG_KEYRING_BACKEND=file
export GOG_KEYRING_PASSWORD="$(secret_lookup gog)"   # never hard-code
```

Credentials are stored at `$XDG_CONFIG_HOME/gogcli/` with mode `0600`;
tokens stay in the OS keyring (or the file backend above).

## Usage

The skill ships no wrapper — the CLI **is** the tool. Most common
entry points:

```bash
# Sanity-check auth + scopes
gog auth doctor --check --json

# Gmail
gog gmail search 'newer_than:7d' --max 10 --json
gog gmail get <messageId> --sanitize-content --json

# Calendar
gog calendar events --today --json

# Drive (read-only audits)
gog drive tree --parent <folderId> --depth 2 --json
gog drive du   --parent <folderId> --max 20 --json

# Docs / Sheets / Slides
gog docs format <docId> --match Status --bold --font-size 18
gog sheets table append <spreadsheetId> Tasks 'Ship README|done'
gog slides create-from-markdown "Weekly update" --content-file slides.md

# Workspace Admin (requires an admin account)
gog --account admin@example.com admin users create ada@example.com \
  --first-name Ada --last-name Lovelace --change-password
```

### Output behavior

- Add `--json` for stable machine-readable JSON on stdout.
- Add `--plain` for TSV (tab-separated, one row per line).
- Errors → stderr; exit code `1` on failure, `0` on success.

## Safety notes

- Never log or commit `client_secret_*.json`, `GOG_KEYRING_PASSWORD`,
  or any token.
- Run `gog auth doctor --check` before any write — sending to the
  wrong account is the highest-impact failure mode.
- Workspace Admin writes (`admin users create`, deletes, OU changes)
  are org-visible and hard to reverse. Confirm before running.
- Prefer read-only verbs (`get`, `read`, `search`, `tree`, `du`,
  `list`) when no write was explicitly authorized.

## Layout

```
googlecli/
├── README.md   # this file
└── SKILL.md    # agent-facing instructions (paperclip)
```

## Reference

- Project site: <https://gogcli.sh>
- Install guide: <https://gogcli.sh/install.html>
- Quickstart (auth): <https://gogcli.sh/quickstart.html>
- Releases: <https://github.com/openclaw/gogcli/releases>
