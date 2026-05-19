#!/usr/bin/env python3
"""Generate PNG images via an Azure AI Foundry image deployment.

This is the canonical entry point referenced by SKILL.md. Endpoint and
API key come from the AZURE_AI_FOUNDRY_ENDPOINT and AZURE_AI_FOUNDRY_API_KEY
environment variables; the deployment name defaults to gpt-image-2 but can
be overridden via AZURE_AI_FOUNDRY_DEPLOYMENT or --deployment.
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path

from openai import OpenAI

DEFAULT_DEPLOYMENT_NAME = "gpt-image-2"
SUPPORTED_SIZES = {"1024x1024", "1024x1536", "1536x1024"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate PNG images from a text prompt using Azure AI Foundry gpt-image-2.",
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
        "--deployment",
        default=os.getenv("AZURE_AI_FOUNDRY_DEPLOYMENT", DEFAULT_DEPLOYMENT_NAME),
        help=(
            "Azure AI Foundry deployment name (default: $AZURE_AI_FOUNDRY_DEPLOYMENT "
            f"or '{DEFAULT_DEPLOYMENT_NAME}')."
        ),
    )
    return parser.parse_args()


def output_path_for(base: Path, index: int, total: int) -> Path:
    if total == 1:
        return base
    return base.with_name(f"{base.stem}-{index + 1}{base.suffix}")


def main() -> int:
    args = parse_args()

    api_key = os.getenv("AZURE_AI_FOUNDRY_API_KEY")
    if not api_key:
        print(
            "ERROR: AZURE_AI_FOUNDRY_API_KEY is not set. Export it before running this script.",
            file=sys.stderr,
        )
        return 2

    endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
    if not endpoint:
        print(
            "ERROR: AZURE_AI_FOUNDRY_ENDPOINT is not set. Export the OpenAI v1 base URL "
            "for your Azure AI Foundry resource (e.g. "
            "https://<resource-name>.services.ai.azure.com/openai/v1).",
            file=sys.stderr,
        )
        return 2

    if args.n < 1:
        print("ERROR: --n must be >= 1", file=sys.stderr)
        return 2

    client = OpenAI(base_url=endpoint, api_key=api_key)

    try:
        response = client.images.generate(
            model=args.deployment,
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
