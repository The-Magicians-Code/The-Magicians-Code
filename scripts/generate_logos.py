#!/usr/bin/env python3
"""Regenerate the tech-stack logo grid in README.md.

Lists the SVG logos in the assets repo, pairs light/dark variants into a
theme-aware <picture>, and rewrites the centered grid (logo with its label
below) between the LOGOS markers in README.md. Run by the
"Update tech-stack logos" GitHub Action; can also be run locally.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

# --- where the logos live ---------------------------------------------------
ASSETS_REPO = "The-Magicians-Code/The-Magicians-Code.github.io"
ASSETS_REF = "main"
ASSETS_PATH = "src/assets/logos"
RAW_BASE = f"https://raw.githubusercontent.com/{ASSETS_REPO}/{ASSETS_REF}/{ASSETS_PATH}"

# --- where the grid is written ----------------------------------------------
README = "README.md"
START = "<!-- LOGOS:START -->"
END = "<!-- LOGOS:END -->"
COLUMNS = 6

# Pretty names for filenames that don't title-case nicely. Anything not listed
# falls back to filename.replace("-", " ").title(), so new logos still render.
LABELS = {
    "aws-amazon-simple-storage-service": "AWS S3",
    "cplusplus": "C++",
    "elasticsearch": "Elasticsearch",
    "gitlab": "GitLab",
    "grafana": "Grafana",
    "gstreamer": "GStreamer",
    "javascript": "JavaScript",
    "nvidia": "NVIDIA",
    "onnx": "ONNX",
    "openapi": "OpenAPI",
    "opencv": "OpenCV",
    "postgresql": "PostgreSQL",
    "pytorch": "PyTorch",
    "sqlite": "SQLite",
    "tensorflow": "TensorFlow",
}


def fetch_filenames() -> list[str]:
    """Return every *.svg filename in the logos directory of the assets repo."""
    url = (
        f"https://api.github.com/repos/{ASSETS_REPO}/contents/{ASSETS_PATH}"
        f"?ref={ASSETS_REF}"
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "readme-logo-gen",
            "Accept": "application/vnd.github+json",
        },
    )
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        entries = json.load(resp)
    return sorted(
        e["name"]
        for e in entries
        if e.get("type") == "file" and e["name"].endswith(".svg")
    )


def label_for(base: str) -> str:
    return LABELS.get(base, base.replace("-", " ").title())


def build_grid(filenames: list[str]) -> str:
    """Build a centered HTML grid: each cell is a logo with its label below.

    A "<base>.svg" with a sibling "<base>.dark.svg" becomes a <picture> that
    swaps to the dark variant under prefers-color-scheme: dark.
    """
    bases = sorted(
        {f[:-4] for f in filenames if f.endswith(".svg") and not f.endswith(".dark.svg")}
    )
    has_dark = {f[: -len(".dark.svg")] for f in filenames if f.endswith(".dark.svg")}

    cells: list[str] = []
    for base in bases:
        label = label_for(base)
        if base in has_dark:
            img = (
                "<picture>"
                f'<source media="(prefers-color-scheme: dark)" '
                f'srcset="{RAW_BASE}/{base}.dark.svg">'
                f'<img height="48" alt="{label}" src="{RAW_BASE}/{base}.svg">'
                "</picture>"
            )
        else:
            img = f'<img height="48" alt="{label}" src="{RAW_BASE}/{base}.svg">'
        cells.append(f'    <td align="center" width="110">{img}<br>{label}</td>')

    lines = ['<table align="center">']
    for i in range(0, len(cells), COLUMNS):
        lines.append("  <tr>")
        lines.extend(cells[i : i + COLUMNS])
        lines.append("  </tr>")
    lines.append("</table>")
    return "\n".join(lines)


def write_readme(grid: str) -> None:
    with open(README, encoding="utf-8") as fh:
        content = fh.read()
    block = f"{START}\n{grid}\n{END}"
    pattern = re.compile(re.escape(START) + ".*?" + re.escape(END), re.S)
    if not pattern.search(content):
        raise SystemExit(f"Markers {START} / {END} not found in {README}")
    with open(README, "w", encoding="utf-8") as fh:
        fh.write(pattern.sub(lambda _: block, content))


def main() -> None:
    filenames = fetch_filenames()
    grid = build_grid(filenames)
    write_readme(grid)
    bases = {f[:-4] for f in filenames if f.endswith(".svg") and not f.endswith(".dark.svg")}
    print(f"Synced {len(bases)} logos from {len(filenames)} files.")


if __name__ == "__main__":
    main()
