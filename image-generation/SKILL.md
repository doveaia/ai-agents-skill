---
name: image-generation
description: >
  Generate PNG images from a text prompt using an Azure AI Foundry image
  deployment (default: gpt-image-2) via the OpenAI Python SDK. Use when the
  agent needs to create illustrations, marketing visuals, thumbnails,
  mockups, icons, social media images, or any other raster image from a
  textual description. Do NOT use for: editing existing images, vector
  graphics (SVG), video, or audio. Do NOT use if the
  AZURE_AI_FOUNDRY_API_KEY or AZURE_AI_FOUNDRY_ENDPOINT environment
  variables are not set — request them from the operator first.
---

# Image Generation (Azure AI Foundry)

This skill produces a PNG file from a text prompt using an image
deployment hosted on Azure AI Foundry (default deployment: `gpt-image-2`).
Agents should invoke the helper script `scripts/generate_image.py` rather
than hand-rolling the API call, so that endpoint, model name, and decoding
logic stay consistent.

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
3. The following environment variables exported. If any are missing, stop
   and ask the operator — **never hard-code secrets or endpoint URLs**.

   | Variable | Required | Description |
   | --- | --- | --- |
   | `AZURE_AI_FOUNDRY_API_KEY` | yes | API key for the Azure AI Foundry resource. |
   | `AZURE_AI_FOUNDRY_ENDPOINT` | yes | Base URL of the OpenAI-compatible endpoint, e.g. `https://<resource-name>.services.ai.azure.com/openai/v1`. |
   | `AZURE_AI_FOUNDRY_DEPLOYMENT` | no | Image deployment name. Defaults to `gpt-image-2`; override via this env var or `--deployment`. |

## Usage

Run the helper script with the prompt and the desired output path:

```bash
export AZURE_AI_FOUNDRY_API_KEY="…"
export AZURE_AI_FOUNDRY_ENDPOINT="https://<resource-name>.services.ai.azure.com/openai/v1"

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
- `--deployment` (optional) — Azure AI Foundry deployment name. Defaults to
  `$AZURE_AI_FOUNDRY_DEPLOYMENT`, then `gpt-image-2`.

The script exits non-zero with a clear error message if any required env
var is missing, the API call fails, or the output cannot be written.

## Canonical Python implementation

The script `scripts/generate_image.py` mirrors this canonical snippet,
which is the source of truth for the API call. Endpoint, API key, and
deployment all come from environment variables so this skill stays
publishable (no secrets or tenant-specific URLs in the repo).

```python
import base64
import os
from openai import OpenAI

endpoint = os.environ["AZURE_AI_FOUNDRY_ENDPOINT"]
api_key = os.environ["AZURE_AI_FOUNDRY_API_KEY"]
deployment_name = os.getenv("AZURE_AI_FOUNDRY_DEPLOYMENT", "gpt-image-2")

client = OpenAI(
    base_url=endpoint,
    api_key=api_key,
)

img = client.images.generate(
    model=deployment_name,
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
