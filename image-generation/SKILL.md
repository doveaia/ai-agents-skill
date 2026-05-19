---
name: image-generation
description: >
  Generate PNG images from a text prompt via any OpenAI-compatible image
  endpoint (official OpenAI API, Azure AI Foundry, or any other provider
  exposing the same Images API). Default model: gpt-image-2. Use when the
  agent needs to create illustrations, marketing visuals, thumbnails,
  mockups, icons, social media images, or any other raster image from a
  textual description. Do NOT use for: editing existing images, vector
  graphics (SVG), video, or audio. Do NOT use if the OPENAI_API_KEY or
  OPENAI_BASE_URL environment variables are not set — request them from
  the operator first.
---

# Image Generation (OpenAI-compatible)

This skill produces a PNG file from a text prompt via any OpenAI-compatible
Images endpoint — official OpenAI API, Azure AI Foundry, or any other
provider implementing the same interface. The default model is
`gpt-image-2`. Agents should invoke the helper script
`scripts/generate_image.py` rather than hand-rolling the API call, so the
base URL, model, and decoding logic stay consistent.

## When to use

Use this skill any time the task requires creating a new image from a
description, including:

- Blog post / newsletter hero images
- YouTube thumbnails
- Social media posts (LinkedIn, Twitter, Instagram)
- Product mockups, concept art, icons, illustrations
- Placeholder visuals while waiting for a designer

## When NOT to use

- Editing or compositing an existing image (this endpoint is generation-only)
- Producing SVG or any vector format (output is always PNG)
- Generating photorealistic depictions of real, identifiable people
- Generating content that violates Azure OpenAI's responsible-AI policy

## Prerequisites

1. `python3` available on the runtime.
2. The `openai` package installed (`pip install openai`).
3. The following environment variables exported. If any required one is
   missing, stop and ask the operator — **never hard-code secrets or
   endpoint URLs**.

   | Variable | Required | Description |
   | --- | --- | --- |
   | `OPENAI_API_KEY` | yes | API key for your OpenAI-compatible provider. |
   | `OPENAI_BASE_URL` | yes | Base URL of the OpenAI-compatible Images endpoint, e.g. `https://api.openai.com/v1` (official OpenAI) or `https://<resource>.services.ai.azure.com/openai/v1` (Azure AI Foundry). |
   | `OPENAI_IMAGE_MODEL` | no | Image model / deployment name. Defaults to `gpt-image-2`; override via this env var or `--model`. |

## Usage

Run the helper script with the prompt and the desired output path:

```bash
export OPENAI_API_KEY="…"
export OPENAI_BASE_URL="https://api.openai.com/v1"
# Optional:
# export OPENAI_IMAGE_MODEL="gpt-image-2"

python3 scripts/generate_image.py \
  --prompt "A cute baby polar bear" \
  --output output.png \
  --size 1024x1024
```

Arguments:

- `--prompt` (required) — the textual description of the image.
- `--output` (optional, default `output.png`) — path where the PNG is written.
- `--size` (optional, default `1024x1024`) — image size. Supported values:
  `1024x1024`, `1024x1536` (portrait), `1536x1024` (landscape).
- `--n` (optional, default `1`) — number of images. When `n > 1`, the script
  appends `-1`, `-2`, … before the file extension.
- `--model` (optional) — image model / deployment name. Defaults to
  `$OPENAI_IMAGE_MODEL`, then `gpt-image-2`.

The script exits non-zero with a clear error message if any required env
var is missing, the API call fails, or the output cannot be written.

## Canonical Python implementation

The script `scripts/generate_image.py` mirrors this canonical snippet,
which is the source of truth for the API call. Base URL, API key, and
model all come from environment variables so this skill stays publishable
(no secrets or tenant-specific URLs in the repo) and works against any
OpenAI-compatible provider.

```python
import base64
import os
from openai import OpenAI

base_url = os.environ["OPENAI_BASE_URL"]
api_key = os.environ["OPENAI_API_KEY"]
model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")

client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

img = client.images.generate(
    model=model,
    prompt="A cute baby polar bear",
    n=1,
    size="1024x1024",
)

image_bytes = base64.b64decode(img.data[0].b64_json)
with open("output.png", "wb") as f:
    f.write(image_bytes)
```

## Prompt-writing guidance

`gpt-image-2` follows prompts literally. For best results:

- Lead with the **subject**, then **style**, then **composition / framing**,
  then **lighting / mood**, then **color palette**.
- State the **aspect ratio** explicitly in words (e.g. "square composition",
  "wide landscape banner") in addition to setting `--size`.
- Include negative constraints ("no text", "no watermark") when needed.
- For brand assets, include the brand name and any required style tokens
  (e.g. "Doveaia teal #0BBFB4 accent, flat vector illustration").

## Reporting back

After generation, the agent should report:

1. The exact prompt used.
2. The output file path(s) written.
3. The size and number of images generated.
4. Any policy refusals or errors from the API, verbatim.
