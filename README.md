# ai-agents-skill

A collection of [Paperclip](https://docs.paperclip.ing) skills used by
Doveaia AI agents. Each skill lives in its own directory containing a
`SKILL.md` (the agent-facing instructions) and any supporting scripts.

## Skills

| Skill | Description |
| --- | --- |
| [`image-generation/`](./image-generation/SKILL.md) | Generate PNG images from a text prompt using an Azure AI Foundry image deployment (default: `gpt-image-2`) via the OpenAI Python SDK. |

## Environment variables

Skills in this repo read all credentials and tenant-specific endpoints
from environment variables — **no secrets or tenant URLs are committed**.
Export the relevant variables for the skills you intend to use.

### `image-generation`

| Variable | Required | Description |
| --- | --- | --- |
| `AZURE_AI_FOUNDRY_API_KEY` | yes | API key for your Azure AI Foundry resource. |
| `AZURE_AI_FOUNDRY_ENDPOINT` | yes | OpenAI-compatible base URL of your Azure AI Foundry resource, e.g. `https://<your-resource-name>.services.ai.azure.com/openai/v1`. |
| `AZURE_AI_FOUNDRY_DEPLOYMENT` | no | Image deployment name. Defaults to `gpt-image-2`. Can also be overridden per-call via `--deployment`. |

Example:

```bash
export AZURE_AI_FOUNDRY_API_KEY="…"
export AZURE_AI_FOUNDRY_ENDPOINT="https://<your-resource-name>.services.ai.azure.com/openai/v1"
# Optional:
# export AZURE_AI_FOUNDRY_DEPLOYMENT="gpt-image-2"
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
