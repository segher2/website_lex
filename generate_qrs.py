#!/usr/bin/env python3
"""
Generate SVG QR codes from a list of strings (URLs, text, etc.).
- Import and call `make_qr_svgs([...])`, OR
- Run from CLI with items or a newline-separated file.

Requires: segno  (pip install segno)
"""

from __future__ import annotations
import argparse
import hashlib
import pathlib
import re
from typing import Iterable, List, Optional
from urllib.parse import urlparse

import segno


def _ensure_url_scheme(s: str) -> str:
    """
    If s looks like a web URL but lacks a scheme, add 'https://'.
    Otherwise return s unchanged.
    """
    s = s.strip()
    if not s:
        return s
    # If it already has a scheme, keep it.
    parsed = urlparse(s)
    if parsed.scheme:
        return s
    # Heuristic: looks like a domain or starts with 'www.'
    if re.match(r"^(www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?$", s):
        return "https://" + s
    return s


def _safe_basename(s: str, max_len: int = 64) -> str:
    """
    Create a filesystem-safe base filename from the input string.
    Keeps a readable hint (domain or first path component) + a short hash.
    """
    hint = s.strip()
    if not hint:
        hint = "empty"

    # Try to extract a meaningful hint (domain or first path piece)
    parsed = urlparse(hint)
    parts: List[str] = []
    if parsed.netloc:
        parts.append(parsed.netloc)
        if parsed.path and parsed.path not in ("/", ""):
            # take first non-empty path segment
            seg = next((p for p in parsed.path.split("/") if p), "")
            if seg:
                parts.append(seg)
    else:
        # Not a URL – use the first 24 chars of the text
        parts.append(hint[:24])

    readable = "-".join(parts) if parts else "item"

    # Sanitize
    readable = re.sub(r"[^A-Za-z0-9._-]+", "-", readable).strip("-._")
    if not readable:
        readable = "item"

    # Short content hash for uniqueness
    short_hash = hashlib.blake2b(hint.encode("utf-8"), digest_size=6).hexdigest()

    base = f"{readable}-{short_hash}"
    if len(base) > max_len:
        base = base[:max_len]

    return base or "qr"


def make_qr_svgs(
    items: Iterable[str],
    out_dir: str | pathlib.Path = "qr_svgs",
    *,
    error: str = "m",          # 'l', 'm', 'q', or 'h'
    scale: int = 10,           # pixel size per module in the SVG
    border: int = 2,           # quiet zone modules
    dark: str = "#000000",     # foreground color
    light: Optional[str] = None,  # None = transparent background
) -> list[pathlib.Path]:
    """
    Generate one SVG QR per item. Returns list of written file paths.
    """
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    written: list[pathlib.Path] = []
    for raw in items:
        if raw is None:
            continue
        text = str(raw).strip()
        if not text:
            continue

        payload = _ensure_url_scheme(text)
        qr = segno.make(payload, error=error)

        fname = _safe_basename(payload) + ".svg"
        fpath = out / fname

        qr.save(
            fpath,
            kind="svg",
            scale=scale,
            border=border,
            dark=dark,
            light=light,
        )
        written.append(fpath)

    return written


def _read_lines_file(path: pathlib.Path) -> list[str]:
    with path.open("r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]


def main():
    parser = argparse.ArgumentParser(
        description="Generate SVG QR codes from a list of strings (URLs/text)."
    )
    parser.add_argument(
        "items",
        nargs="*",
        help="Items to encode. If omitted, use --file to read newline-separated items.",
    )
    parser.add_argument(
        "-f", "--file",
        type=pathlib.Path,
        help="Path to a text file with one item per line.",
    )
    parser.add_argument(
        "-o", "--out-dir",
        default="qr_svgs",
        help="Output directory (default: qr_svgs)",
    )
    parser.add_argument(
        "--error",
        choices=["l", "m", "q", "h"],
        default="m",
        help="Error correction level (default: m)",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=10,
        help="SVG module scale (default: 10)",
    )
    parser.add_argument(
        "--border",
        type=int,
        default=2,
        help="Quiet zone in modules (default: 2)",
    )
    parser.add_argument(
        "--dark",
        default="#000000",
        help="Foreground color (default: #000000)",
    )
    parser.add_argument(
        "--light",
        default=None,
        help="Background color; omit/None for transparent (default: None)",
    )

    args = parser.parse_args()

    items: List[str] = list(args.items)
    if args.file:
        items.extend(_read_lines_file(args.file))

    if not items:
        parser.error("No items provided. Pass items as args or via --file path.")

    written = make_qr_svgs(
        items,
        out_dir=args.out_dir,
        error=args.error,
        scale=args.scale,
        border=args.border,
        dark=args.dark,
        light=args.light,
    )

    print(f"Wrote {len(written)} SVG(s) to: {pathlib.Path(args.out_dir).resolve()}")
    for p in written:
        print(p)


if __name__ == "__main__":
    main()
