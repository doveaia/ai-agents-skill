#!/usr/bin/env python3
"""Generate PNG images via any OpenAI-compatible image endpoint.

This is the canonical entry point referenced by SKILL.md. The script
reads its config from one of two env-var namespaces:

  Primary (standard OpenAI SDK names):
    OPENAI_API_KEY
    OPENAI_BASE_URL
    OPENAI_IMAGE_MODEL    (optional, default: gpt-image-2)

  Image-scoped override (avoids clashing with other tools that already
  use OPENAI_API_KEY for api.openai.com):
    OPENAI_IMAGE_API_KEY
    OPENAI_IMAGE_BASE_URL
    OPENAI_IMAGE_MODEL    (optional, default: gpt-image-2)

The two namespaces are resolved atomically: if either
OPENAI_IMAGE_API_KEY or OPENAI_IMAGE_BASE_URL is set, the script uses
the OPENAI_IMAGE_* bundle (and errors if its counterpart is missing).
Otherwise it uses OPENAI_API_KEY + OPENAI_BASE_URL. Namespaces are never
mixed, so a key from one provider can never accidentally pair with the
base URL of another.
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


def resolve_credentials() -> tuple[str | None, str | None, str | None]:
    """Resolve (api_key, base_url, error_message).

    If either OPENAI_IMAGE_API_KEY or OPENAI_IMAGE_BASE_URL is set, the
    OPENAI_IMAGE_* bundle is used and the script errors if its
    counterpart is missing. Otherwise the standard OPENAI_API_KEY /
    OPENAI_BASE_URL bundle is used. Namespaces are never mixed.
    """
    image_key = os.getenv("OPENAI_IMAGE_API_KEY")
    image_url = os.getenv("OPENAI_IMAGE_BASE_URL")

    if image_key or image_url:
        if not image_key:
            return None, None, (
                "OPENAI_IMAGE_BASE_URL is set but OPENAI_IMAGE_API_KEY is not. "
                "Set both, or unset both to fall back to the OPENAI_* namespace."
            )
        if not image_url:
            return None, None, (
                "OPENAI_IMAGE_API_KEY is set but OPENAI_IMAGE_BASE_URL is not. "
                "Set both, or unset both to fall back to the OPENAI_* namespace."
            )
        return image_key, image_url, None

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    if not api_key or not base_url:
        missing = []
        if not api_key:
            missing.append("OPENAI_API_KEY (or OPENAI_IMAGE_API_KEY)")
        if not base_url:
            missing.append("OPENAI_BASE_URL (or OPENAI_IMAGE_BASE_URL)")
        return None, None, "Missing required env var(s): " + ", ".join(missing)
    return api_key, base_url, None


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

    api_key, base_url, err = resolve_credentials()
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
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
