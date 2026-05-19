# ai-agents-skill

A collection of [Paperclip](https://docs.paperclip.ing) skills used by
Doveaia AI agents. Each skill lives in its own directory containing a
`SKILL.md` (agent-facing instructions), a `README.md` (human-facing quick
start), and any supporting scripts.

## Skills

| Skill | What it does | Path |
| --- | --- | --- |
| `image-generation` | Generate PNG images from a text prompt via any OpenAI-compatible image endpoint (official OpenAI, Azure AI Foundry, or any other provider). Default model: `gpt-image-2`. | [`image-generation/`](./image-generation/) |

For setup, environment variables, and usage, see each skill's `README.md`.
