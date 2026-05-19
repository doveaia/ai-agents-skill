---
name: googlecli
description: >
  Drive Google Workspace from the terminal via the official `gog` CLI
  (https://gogcli.sh) — Gmail, Calendar, Drive, Docs, Sheets, Slides,
  Contacts, Tasks, Admin, etc. Use when the agent needs to search a
  mailbox, list calendar events, audit a Drive folder, read or edit a
  Doc / Sheet / Slide, or create a user in Workspace Admin. Do NOT use
  for: anything requiring a Google graphical UI, services not exposed by
  Google APIs, or providers other than Google. Do NOT use if `gog` is
  not on PATH, no OAuth client is registered (`gog auth credentials`),
  or no account is authorized (`gog auth add`) — surface the gap to the
  operator first.
---

# gog CLI (Google Workspace)

This skill teaches agents how to drive the official `gog` CLI
non-interactively against Google Workspace. The CLI is the source of
truth — there is no Python or shell wrapper here. The agent invokes
`gog ...` as a subprocess and parses the JSON / TSV it prints on
stdout.

## Prerequisites

1. `gog` available on `PATH` (`gog --version` returns a version).
   Install via:

   ```bash
   brew install gogcli                              # macOS / Linux (Homebrew)
   docker run --rm ghcr.io/openclaw/gogcli:latest version  # containerized
   ```

   Windows: download `gogcli_<version>_windows_amd64.zip` from
   <https://github.com/openclaw/gogcli/releases>, extract `gog.exe`,
   add to PATH. Source build:
   `git clone https://github.com/openclaw/gogcli && cd gogcli && make`.

2. An OAuth **client** registered as "Desktop app" in Google Cloud
   Console, downloaded as a `client_secret_*.json`, and imported once:

   ```bash
   gog auth credentials ~/Downloads/client_secret_*.json
   ```

3. At least one **authorized account** with the scopes the workflow
   needs:

   ```bash
   gog auth add you@gmail.com \
     --services gmail,calendar,drive,docs,sheets,contacts
   ```

   Headless variants:
   - `--manual` → prints a URL, paste the consent code back.
   - `--remote --step 1` (on the headless host) + `--step 2` (on the
     machine with a browser) → two-step flow.

4. (Recommended) A default account so the agent does not have to pass
   `--account` on every call:

   ```bash
   export GOG_ACCOUNT=you@gmail.com
   gog auth alias set default you@gmail.com
   ```

5. (Headless / CI) When no GUI keyring is available, use a file
   backend with a password supplied out of band (do not bake into
   images or scripts):

   ```bash
   export GOG_KEYRING_BACKEND=file
   export GOG_KEYRING_PASSWORD="$(secret_lookup gog)"
   ```

## How the CLI behaves with agents

- Add `--json` to **any** command to force stable JSON on stdout.
  Errors go to stderr, exit code `1` on any failure, `0` on success.
- Add `--plain` for TSV (one row per line, tab-separated columns).
  Useful when piping to `cut` / `awk` for cheap parsing.
- Credentials live in `$XDG_CONFIG_HOME/gogcli/` (mode `0600`); refresh
  tokens are kept in the OS keyring (Keychain / Secret Service /
  Credential Manager).
- Refresh tokens issued by an OAuth app stuck in **External / Testing**
  expire after 7 days. For long-running agents the operator must
  publish the app — surface this if you see repeated re-auth failures.
- Multi-account: pass `--account other@example.com`. Multi-client:
  `--client <name>`. See `gog auth list --check`.

Before the first call of any workflow, **always run**:

```bash
gog auth doctor --check --json
```

and verify the target account / services come back healthy. If not,
stop and surface the failure verbatim.

## Service quick reference

All examples use `--json` so the agent gets parseable output. Drop it
in interactive shells if a human will read the result.

### Gmail

```bash
gog gmail search 'newer_than:7d from:billing@*' --max 10 --json
gog gmail get <messageId> --sanitize-content --json
```

`--sanitize-content` strips tracking pixels and external image fetches
from message bodies — use it whenever you forward a body to an LLM.

### Calendar

```bash
gog calendar events --today --json
gog calendar events --from 2026-05-19 --to 2026-05-26 --json
```

### Drive (read-only audits)

```bash
gog drive tree --parent <folderId> --depth 2 --json
gog drive du   --parent <folderId> --max 20 --json
```

`drive tree` walks the folder; `drive du` ranks children by size. Both
are read-only.

### Docs

```bash
gog docs get <docId> --json                         # read
gog docs format <docId> --match Status --bold --font-size 18
```

Targeted edits (`--match <text>` + style flags) are safer than
full-document rewrites — they leave surrounding content untouched.

### Sheets

```bash
gog sheets read <spreadsheetId> 'Tasks!A1:D' --json
gog sheets table append <spreadsheetId> Tasks 'Ship README|done'
```

The pipe `|` separator in `table append` is the column delimiter,
not a shell pipe — quote the whole argument.

### Slides

```bash
gog slides create-from-markdown "Weekly update" \
  --content-file slides.md --json
```

Markdown → deck. The CLI does the layout; do not try to position
shapes manually.

### Admin (Workspace)

Requires `--account` with an admin role on the workspace:

```bash
gog --account admin@example.com admin users create ada@example.com \
  --first-name Ada --last-name Lovelace --change-password
gog --account admin@example.com admin orgunits list --type all --json
```

`--change-password` forces a password reset on first login — leave it
on unless the operator explicitly says otherwise.

## Discovery

`gog --help` and `gog <subcommand> --help` enumerate flags. For a
machine-readable command tree, use the per-command `--json` and
inspect the response shape — there is no documented `gog commands`
dump.

## Safety rules for agents

1. **Never** log, echo, or commit `client_secret_*.json`,
   `GOG_KEYRING_PASSWORD`, or any access/refresh token. The CLI
   protects them at rest; do not undo that.
2. **Confirm the right account** with `gog auth doctor --check --json`
   before any write (`docs format`, `sheets table append`,
   `slides create-from-markdown`, `admin users create`). Sending to
   the wrong tenant is the highest-impact failure mode.
3. **Prefer read-only verbs** (`get`, `read`, `search`, `tree`, `du`,
   `list`) when the operator has not explicitly approved a write.
4. **Admin writes** (`admin users create`, deletes, OU changes) are
   org-visible and hard to reverse — confirm with the operator and
   echo the exact command back before running.
5. **Drive deletes / moves** affect shared state. If the operator asks
   for cleanup, propose the list of targets first and wait for
   approval, then act.
6. If `gog auth doctor --check` reports any failure, stop and surface
   the output verbatim. Common causes: expired refresh token
   (re-run `gog auth add`), revoked scope, missing service in
   `--services` list at the original add.

## Reporting back

After any send or mutation, the agent should report:

1. The command run (with secrets redacted).
2. The JSON response (or the error JSON from stderr).
3. For Gmail/Docs/Sheets/Slides writes: the resource ID and a one-line
   summary of what changed.
4. For admin writes: the affected user/OU and a reminder that the
   change is org-visible.
