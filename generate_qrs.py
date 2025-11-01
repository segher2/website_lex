#!/usr/bin/env python3
"""
Generate transparent SVG QR codes for each immediate subdirectory in a root folder.

For each dir '01_La17_20a' we generate a QR for:
    https://www.lexterbraak.nl/01_La17_20a/

Output SVGs are saved in ./qr_svgs (or --out-dir).
The SVG filename matches the directory name exactly (01_La17_20a.svg).

All QR codes are rendered with the same module size (same grid),
based on the largest required version among all dirs.
"""

from __future__ import annotations
import argparse
import pathlib
from typing import List, Dict
import segno


BASE_URL = "https://www.lexterbraak.nl/"


def get_immediate_subdirs(root: pathlib.Path) -> List[str]:
    """
    Return a sorted list of folder names directly under `root`.
    Only directories, no recursion.
    """
    return sorted(
        [p.name for p in root.iterdir() if p.is_dir()]
    )


def make_payloads_from_dirs(dirnames: List[str]) -> Dict[str, str]:
    """
    Map dirname -> full URL like
    '01_La17_20a' -> 'https://www.lexterbraak.nl/01_La17_20a/'
    """
    out: Dict[str, str] = {}
    for d in dirnames:
        # ensure trailing slash
        url = BASE_URL + d.strip("/") + "/"
        out[d] = url
    return out


def find_max_symbol_size(payloads: Dict[str, str]) -> int:
    """
    Generate temp segno QR objects for all payloads and
    return the maximum matrix size (number of modules per side).
    """
    max_size = 0
    for text in payloads.values():
        qr = segno.make(text, error="m")
        size = qr.symbol_size()[0]  # (width, height)
        if size > max_size:
            max_size = size
    return max_size


def save_qr_svgs_uniform(
    payloads: Dict[str, str],
    out_dir: pathlib.Path,
    *,
    error: str = "m",
    scale: int = 10,
    border: int = 2,
    dark: str = "#000000",
    light: str | None = None,
) -> List[pathlib.Path]:
    """
    Render all payloads as SVG with the SAME symbol size
    (max version / module count across all).
    Return list of written file paths.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. figure out max symbol size needed
    max_size = find_max_symbol_size(payloads)

    written: List[pathlib.Path] = []

    for dirname, text in payloads.items():
        # segno.make() will choose the minimal version that fits.
        # We can't directly "upscale" version after creation,
        # but we can force same grid size by telling segno not to
        # increase error correction automatically and then exporting
        # at a fixed scale. However, different data can still end up
        # with different version numbers (grid sizes).
        #
        # Trick: we re-make larger versions by padding via "version"
        # argument. segno lets us pass `version` to force at least that size.
        #
        # We pick a version that matches max_size.
        #
        # version '1' is 21x21 modules, and each increment adds 4 modules
        # per side (25x25, 29x29, ...). We'll reverse-engineer which
        # version number corresponds to max_size.

        def version_from_size(sz: int) -> int:
            # QR Version n has size = 21 + 4*(n-1)
            # Solve n = ((sz - 21) / 4) + 1
            n_float = ((sz - 21) / 4.0) + 1
            n = int(round(n_float))
            return max(n, 1)

        target_version = version_from_size(max_size)

        qr = segno.make(text, error=error, version=target_version, boost_error=False)

        # double-check it's at least max_size; segno won't make it *smaller*
        # than requested version when boost_error=False.
        # (If for some reason it's bigger (rare), that's fine,
        # all will still be consistent because target_version is same for all.)

        fname = f"{dirname}.svg"
        fpath = out_dir / fname

        qr.save(
            fpath,
            kind="svg",
            scale=scale,
            border=border,
            dark=dark,
            light=light,  # None -> transparent background
        )
        written.append(fpath)

    return written


def main():
    parser = argparse.ArgumentParser(
        description="Generate uniform transparent SVG QR codes for each subdirectory."
    )
    parser.add_argument(
        "root",
        type=pathlib.Path,
        help="Path that contains the numbered folders (flat, no recursion).",
    )
    parser.add_argument(
        "-o", "--out-dir",
        default="qr_svgs",
        help="Output directory for SVGs (default: qr_svgs)",
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
        help="Background color; leave None for transparent (default: None)",
    )

    args = parser.parse_args()

    subdirs = get_immediate_subdirs(args.root)
    if not subdirs:
        parser.error("No subdirectories found in the provided root.")

    payloads = make_payloads_from_dirs(subdirs)

    written = save_qr_svgs_uniform(
        payloads,
        out_dir=pathlib.Path(args.out_dir),
        error="m",
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
