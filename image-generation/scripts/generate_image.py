#!/usr/bin/env python3
"""Generate PNG images via any OpenAI-compatible image endpoint.

This is the canonical entry point referenced by SKILL.md. The script uses
the standard OpenAI SDK environment variables so it works against the
official OpenAI API, Azure AI Foundry, or any other OpenAI-compatible
provider without code changes:

- OPENAI_API_KEY       — API key for the provider
- OPENAI_BASE_URL      — base URL of the OpenAI-compatible endpoint
- OPENAI_IMAGE_MODEL   — model / deployment name (default: gpt-image-2)
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path

from openai import OpenAI

DEFAULT_IMAGE_MODEL = "gpt-image-2"
SUPPORTED_SIZES = {"1024x1024", "1024x1536", "1536x1024"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate PNG images from a text prompt via any OpenAI-compatible endpoint.",
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Text prompt describing the image to generate.",
    )
    parser.add_argument(
        "--output",
        default="output.png",
        help="Output PNG path (default: output.png). When --n > 1, an index is inserted before the extension.",
    )
    parser.add_argument(
        "--size",
        default="1024x1024",
        choices=sorted(SUPPORTED_SIZES),
        help="Image size (default: 1024x1024).",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=1,
        help="Number of images to generate (default: 1).",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_IMAGE_MODEL", DEFAULT_IMAGE_MODEL),
        help=(
            "Image model / deployment name (default: $OPENAI_IMAGE_MODEL "
            f"or '{DEFAULT_IMAGE_MODEL}')."
        ),
    )
    return parser.parse_args()


def output_path_for(base: Path, index: int, total: int) -> Path:
    if total == 1:
        return base
    return base.with_name(f"{base.stem}-{index + 1}{base.suffix}")


def main() -> int:
    args = parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(
            "ERROR: OPENAI_API_KEY is not set. Export it before running this script.",
            file=sys.stderr,
        )
        return 2

    base_url = os.getenv("OPENAI_BASE_URL")
    if not base_url:
        print(
            "ERROR: OPENAI_BASE_URL is not set. Export the OpenAI-compatible base URL "
            "of your provider (e.g. https://api.openai.com/v1 for OpenAI, or "
            "https://<resource-name>.services.ai.azure.com/openai/v1 for Azure AI Foundry).",
            file=sys.stderr,
        )
        return 2

    if args.n < 1:
        print("ERROR: --n must be >= 1", file=sys.stderr)
        return 2

    client = OpenAI(base_url=base_url, api_key=api_key)

    try:
        response = client.images.generate(
            model=args.model,
            prompt=args.prompt,
            n=args.n,
            size=args.size,
        )
    except Exception as exc:
        print(f"ERROR: image generation failed: {exc}", file=sys.stderr)
        return 1

    base_path = Path(args.output)
    base_path.parent.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    for i, item in enumerate(response.data):
        if not item.b64_json:
            print(f"ERROR: image {i + 1} has no b64_json payload", file=sys.stderr)
            return 1
        image_bytes = base64.b64decode(item.b64_json)
        path = output_path_for(base_path, i, args.n)
        path.write_bytes(image_bytes)
        written.append(str(path))

    print(f"Generated {len(written)} image(s):")
    for p in written:
        print(f"  - {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
