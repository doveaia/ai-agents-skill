# ai-agents-skill

A collection of [Paperclip](https://docs.paperclip.ing) skills used by
Doveaia AI agents. Each skill lives in its own directory containing a
`SKILL.md` (agent-facing instructions), a `README.md` (human-facing quick
start), and any supporting scripts.

## Skills

| Skill | What it does | Path |
| --- | --- | --- |
| `googlecli` | Drive Google Workspace (Gmail, Calendar, Drive, Docs, Sheets, Slides, Contacts, Tasks, Admin, …) via the official [`gog` CLI](https://gogcli.sh). | [`googlecli/`](./googlecli/) |
| `image-generation` | Generate PNG images from a text prompt via any OpenAI-compatible image endpoint (official OpenAI, Azure AI Foundry, or any other provider). Default model: `gpt-image-2`. | [`image-generation/`](./image-generation/) |
| `resend` | Send transactional emails, manage domains, audiences, contacts, broadcasts, API keys, and webhooks via the official [Resend CLI](https://resend.com/changelog/cli). | [`resend/`](./resend/) |
| `session-restart` | Bail out of a session broken by tooling/infrastructure (adapter_failed, remote compaction 404, deployment-not-found) — persist a handover and ask the operator to start a fresh session instead of looping retries. | [`session-restart/`](./session-restart/) |

For setup, environment variables, and usage, see each skill's `README.md`.
