# image-generation

Generate PNG images from a text prompt via any OpenAI-compatible image
endpoint — official OpenAI API, Azure AI Foundry, or any other provider
exposing the same Images API. Default model: `gpt-image-2`.

> Agent-facing instructions live in [`SKILL.md`](./SKILL.md). This file
> is the human-facing quick start.

## Prerequisites

- Python 3.9+
- `pip install openai`

## Environment variables

The script accepts two interchangeable namespaces — pick whichever fits
your environment. **Pick one. Don't mix.** Namespaces are resolved
atomically so a key from one provider can never accidentally pair with
the base URL of another.

### Option A — standard OpenAI namespace

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | yes | API key for your OpenAI-compatible provider. |
| `OPENAI_BASE_URL` | yes | Base URL of the OpenAI-compatible Images endpoint. |
| `OPENAI_IMAGE_MODEL` | no | Image model / deployment name. Defaults to `gpt-image-2`. |

Use this if no other tool on your system already owns `OPENAI_API_KEY`.

### Option B — image-scoped namespace (recommended when `OPENAI_*` is taken)

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_IMAGE_API_KEY` | yes | API key for your OpenAI-compatible image provider. |
| `OPENAI_IMAGE_BASE_URL` | yes | Base URL of the OpenAI-compatible Images endpoint. |
| `OPENAI_IMAGE_MODEL` | no | Image model / deployment name. Defaults to `gpt-image-2`. |

Use this when `OPENAI_API_KEY` is already exported for another tool
(e.g. one pointing at `api.openai.com`) and you don't want this skill
to inherit it. As soon as the script sees either
`OPENAI_IMAGE_API_KEY` or `OPENAI_IMAGE_BASE_URL`, it ignores the
`OPENAI_*` namespace entirely and requires its counterpart to also be
set.

### Examples — set the base URL to whichever provider you use

```bash
# Official OpenAI
…BASE_URL="https://api.openai.com/v1"

# Azure AI Foundry (OpenAI v1 compatibility surface)
…BASE_URL="https://<your-resource-name>.services.ai.azure.com/openai/v1"

# Any other OpenAI-compatible provider
…BASE_URL="https://<provider-host>/v1"
```

Full export, Option B (image-scoped):

```bash
export OPENAI_IMAGE_API_KEY="…"
export OPENAI_IMAGE_BASE_URL="https://<your-resource-name>.services.ai.azure.com/openai/v1"
# Optional:
# export OPENAI_IMAGE_MODEL="gpt-image-2"
```

To persist these for future shells, add the `export` lines to your
`~/.zshrc` (zsh) or `~/.bashrc` (bash) and reload with `source <file>`.

## Usage

```bash
python3 scripts/generate_image.py \
  --prompt "A cute baby polar bear on an iceberg" \
  --output output.png \
  --size 1024x1024
```

### Arguments

- `--prompt` (required) — the textual description of the image.
- `--output` (optional, default `output.png`) — path where the PNG is written.
- `--size` (optional, default `1024x1024`) — supported values: `1024x1024`,
  `1024x1536` (portrait), `1536x1024` (landscape).
- `--n` (optional, default `1`) — number of images. When `n > 1`, the script
  appends `-1`, `-2`, … before the file extension.
- `--model` (optional) — image model / deployment name. Defaults to
  `$OPENAI_IMAGE_MODEL`, then `gpt-image-2`.

The script exits non-zero with a clear error message if any required env
var is missing, the API call fails, or the output cannot be written.

## Layout

```
image-generation/
├── README.md                    # this file
├── SKILL.md                     # agent-facing instructions (paperclip)
└── scripts/
    └── generate_image.py        # CLI wrapper around the OpenAI SDK
```
