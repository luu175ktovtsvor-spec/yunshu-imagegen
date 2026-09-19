#!/usr/bin/env python3
"""Generate or edit images through a Yunshu OpenAI-compatible Images API."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import mimetypes
import os
import re
import struct
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zlib
from pathlib import Path


DEFAULT_BASE_URL = "https://api.zzyppz.cn/v1"
DEFAULT_MODEL = "gpt-image-2"
MAX_ERROR_BODY = 1200


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def read_codex_provider() -> tuple[str | None, str | None]:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    config_path = codex_home / "config.toml"
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None, None

    providers = config.get("model_providers", {})
    if not isinstance(providers, dict):
        return None, None
    for provider in providers.values():
        if not isinstance(provider, dict):
            continue
        base_url = str(provider.get("base_url", "")).strip()
        if "api.zzyppz.cn" not in base_url:
            continue
        token = str(provider.get("experimental_bearer_token", "")).strip()
        return base_url or None, token or None
    return None, None


def resolve_config() -> tuple[str, str]:
    config_url, config_key = read_codex_provider()
    api_key = os.environ.get("YUNSHU_API_KEY", "").strip() or (config_key or "")
    if not api_key:
        raise SystemExit(
            "YUNSHU_API_KEY is not set and no Yunshu provider key was found in "
            "$CODEX_HOME/config.toml"
        )

    base_url = os.environ.get("YUNSHU_BASE_URL", "").strip() or config_url or DEFAULT_BASE_URL
    base_url = base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url += "/v1"
    return base_url, api_key


def validate_size(value: str) -> str:
    if value == "auto":
        return value
    if not re.fullmatch(r"\d+x\d+", value):
        raise argparse.ArgumentTypeError("size must be auto or WIDTHxHEIGHT")
    width, height = (int(part) for part in value.split("x"))
    if width < 16 or height < 16 or width > 3840 or height > 3840:
        raise argparse.ArgumentTypeError("size must be between 16 and 3840 pixels per edge")
    return value


def request_json(url: str, api_key: str, payload: dict[str, object]) -> dict[str, object]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    return read_response(request)


def multipart_body(fields: dict[str, str], file_path: Path) -> tuple[bytes, str]:
    boundary = f"----yunshu-imagegen-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for key, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode(),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    chunks.extend(
        [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="image"; '
                f'filename="{file_path.name}"\r\n'
            ).encode(),
            f"Content-Type: {mime}\r\n\r\n".encode(),
            file_path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def request_edit(
    url: str,
    api_key: str,
    fields: dict[str, str],
    image_path: Path,
) -> dict[str, object]:
    body, content_type = multipart_body(fields, image_path)
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": content_type,
            "Accept": "application/json",
        },
        method="POST",
    )
    return read_response(request)


def read_response(request: urllib.request.Request) -> dict[str, object]:
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            raw = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read(MAX_ERROR_BODY).decode("utf-8", errors="replace")
        raise SystemExit(f"Yunshu API returned HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise SystemExit(f"Yunshu API request failed: {error.reason}") from error
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SystemExit("Yunshu API returned a non-JSON response") from error
    if not isinstance(parsed, dict):
        raise SystemExit("Yunshu API returned an unexpected JSON shape")
    return parsed


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", binascii.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def normalize_opaque_png(path: Path) -> None:
    """Convert an 8-bit non-interlaced RGBA PNG to RGB.

    Some OpenAI-compatible upstreams return an opaque request with a partially
    transparent alpha channel. Dropping that channel preserves the generated
    colors and prevents viewers from compositing the whole poster against white.
    Unsupported PNG variants are left unchanged.
    """
    raw_png = path.read_bytes()
    if not raw_png.startswith(PNG_SIGNATURE):
        return

    chunks: list[tuple[bytes, bytes]] = []
    idat = bytearray()
    ihdr: tuple[int, int, int, int, int, int, int] | None = None
    offset = len(PNG_SIGNATURE)
    while offset + 12 <= len(raw_png):
        length = struct.unpack(">I", raw_png[offset : offset + 4])[0]
        chunk_type = raw_png[offset + 4 : offset + 8]
        start = offset + 8
        end = start + length
        if end + 4 > len(raw_png):
            return
        data = raw_png[start:end]
        offset = end + 4
        if chunk_type == b"IHDR":
            if length != 13:
                return
            ihdr = struct.unpack(">IIBBBBB", data)
            chunks.append((chunk_type, data))
        elif chunk_type == b"IDAT":
            idat.extend(data)
        elif chunk_type != b"IEND":
            chunks.append((chunk_type, data))
        if chunk_type == b"IEND":
            break

    if ihdr is None:
        return
    width, height, bit_depth, color_type, _, _, interlace = ihdr
    if bit_depth != 8 or color_type not in (4, 6) or interlace != 0:
        return

    channels = 2 if color_type == 4 else 4
    stride = width * channels
    try:
        decoded = zlib.decompress(bytes(idat))
    except zlib.error:
        return
    if len(decoded) != height * (stride + 1):
        return

    def paeth(a: int, b: int, c: int) -> int:
        estimate = a + b - c
        pa = abs(estimate - a)
        pb = abs(estimate - b)
        pc = abs(estimate - c)
        if pa <= pb and pa <= pc:
            return a
        return b if pb <= pc else c

    rows: list[bytes] = []
    previous = bytearray(stride)
    cursor = 0
    for _ in range(height):
        filter_type = decoded[cursor]
        cursor += 1
        row = bytearray(decoded[cursor : cursor + stride])
        cursor += stride
        if filter_type not in (0, 1, 2, 3, 4):
            return
        for index in range(stride):
            left = row[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                row[index] = (row[index] + left) & 0xFF
            elif filter_type == 2:
                row[index] = (row[index] + above) & 0xFF
            elif filter_type == 3:
                row[index] = (row[index] + ((left + above) // 2)) & 0xFF
            elif filter_type == 4:
                row[index] = (row[index] + paeth(left, above, upper_left)) & 0xFF
        if color_type == 6:
            rgb_row = bytes(row[index] for index in range(stride) if (index % 4) != 3)
        else:
            rgb_row = bytes(channel for value in row[0::2] for channel in (value, value, value))
        rows.append(rgb_row)
        previous = row

    # Re-encode as RGB with filter type 0. This makes the result opaque while
    # keeping the generated RGB values unchanged.
    rgb_data = b"".join(b"\x00" + row for row in rows)
    new_ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    output = bytearray(PNG_SIGNATURE)
    output.extend(_png_chunk(b"IHDR", new_ihdr))
    for chunk_type, data in chunks:
        if chunk_type in (b"IHDR", b"IDAT"):
            continue
        output.extend(_png_chunk(chunk_type, data))
    output.extend(_png_chunk(b"IDAT", zlib.compress(rgb_data, level=9)))
    output.extend(_png_chunk(b"IEND", b""))
    path.write_bytes(output)


def save_result(response: dict[str, object], output: Path, *, force_opaque: bool) -> None:
    data = response.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise SystemExit("Yunshu API response did not contain an image result")
    item = data[0]
    output.parent.mkdir(parents=True, exist_ok=True)
    b64_value = item.get("b64_json")
    if isinstance(b64_value, str) and b64_value:
        try:
            output.write_bytes(base64.b64decode(b64_value, validate=True))
        except (ValueError, base64.binascii.Error) as error:
            raise SystemExit("Yunshu API returned invalid b64_json image data") from error
    else:
        image_url = item.get("url")
        if isinstance(image_url, str) and image_url:
            request = urllib.request.Request(image_url, headers={"Accept": "image/*"})
            try:
                with urllib.request.urlopen(request, timeout=180) as response_stream:
                    output.write_bytes(response_stream.read())
            except (urllib.error.URLError, urllib.error.HTTPError) as error:
                raise SystemExit(f"Failed to download generated image: {error}") from error
        else:
            raise SystemExit("Yunshu API response did not contain b64_json or url")

    if force_opaque:
        normalize_opaque_png(output)


def common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--prompt", required=True, help="Image prompt")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Images API model")
    parser.add_argument("--size", default="auto", type=validate_size, help="auto or WIDTHxHEIGHT")
    parser.add_argument("--background", default="opaque", choices=("opaque", "transparent"))
    parser.add_argument("--output", required=True, type=Path, help="Absolute or relative output PNG path")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate a new image")
    common_arguments(generate)

    edit = subparsers.add_parser("edit", help="Edit/composite an input image")
    common_arguments(edit)
    edit.add_argument("--image", required=True, type=Path, help="Input image path")

    args = parser.parse_args()
    base_url, api_key = resolve_config()
    if args.command == "generate":
        payload = {
            "model": args.model,
            "prompt": args.prompt,
            "size": args.size,
            "background": args.background,
            "response_format": "b64_json",
        }
        response = request_json(f"{base_url}/images/generations", api_key, payload)
    else:
        if not args.image.is_file():
            raise SystemExit(f"Input image not found: {args.image}")
        fields = {
            "model": args.model,
            "prompt": args.prompt,
            "size": args.size,
            "background": args.background,
            "response_format": "b64_json",
        }
        response = request_edit(f"{base_url}/images/edits", api_key, fields, args.image)

    save_result(response, args.output, force_opaque=args.background == "opaque")
    print(json.dumps({"output": str(args.output.resolve()), "model": args.model}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
