# ai-agents-skill

A collection of [Paperclip](https://docs.paperclip.ing) skills used by
Doveaia AI agents. Each skill lives in its own directory containing a
`SKILL.md` (the agent-facing instructions) and any supporting scripts.

## Skills

| Skill | Description |
| --- | --- |
| [`image-generation/`](./image-generation/SKILL.md) | Generate PNG images from a text prompt via any OpenAI-compatible image endpoint (official OpenAI, Azure AI Foundry, or any other provider). Default model: `gpt-image-2`. |

## Environment variables

Skills in this repo read all credentials and provider-specific endpoints
from environment variables — **no secrets or tenant URLs are committed**.
Export the relevant variables for the skills you intend to use.

### `image-generation`

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | yes | API key for your OpenAI-compatible provider. |
| `OPENAI_BASE_URL` | yes | Base URL of the OpenAI-compatible Images endpoint (see examples below). |
| `OPENAI_IMAGE_MODEL` | no | Image model / deployment name. Defaults to `gpt-image-2`. Can also be overridden per-call via `--model`. |

Examples — set `OPENAI_BASE_URL` to whichever provider you use:

```bash
# Official OpenAI
export OPENAI_BASE_URL="https://api.openai.com/v1"

# Azure AI Foundry (OpenAI v1 compatibility surface)
export OPENAI_BASE_URL="https://<your-resource-name>.services.ai.azure.com/openai/v1"

# Any other OpenAI-compatible provider
export OPENAI_BASE_URL="https://<provider-host>/v1"
```

Then:

```bash
export OPENAI_API_KEY="…"
# Optional:
# export OPENAI_IMAGE_MODEL="gpt-image-2"
```

To persist these for future shells, add the `export` lines to your
`~/.zshrc` (zsh) or `~/.bashrc` (bash) and reload with `source <file>`.

## Requirements

- Python 3.9+
- `pip install openai`

## Usage

Each skill is self-contained. See its `SKILL.md` for agent-facing
instructions and the scripts it ships with. For example, to generate an
image with the `image-generation` skill once the env vars above are set:

```bash
python3 image-generation/scripts/generate_image.py \
  --prompt "A cute baby polar bear on an iceberg" \
  --output output.png \
  --size 1024x1024
```

## Using these skills with Paperclip

This repository follows the Paperclip skill layout described in
[Writing a Skill](https://docs.paperclip.ing). Each top-level folder is a
skill containing a `SKILL.md` with YAML frontmatter (`name`,
`description`) and optional supporting files under `scripts/` or
`references/`. Adapters (e.g. `claude_local`, `codex_local`) are
responsible for making these skills discoverable to their agent runtime.

## License

See [LICENSE](./LICENSE) if present, otherwise treat as “All rights
reserved” until one is added.
