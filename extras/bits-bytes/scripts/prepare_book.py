#!/usr/bin/env python3
"""Prepare an mdBook input tree from the GitHub-readable canonical chapters."""
from pathlib import Path
import re
import shutil
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / ".book-src"
REPO = "https://github.com/Waikizashi/russian-rustbook/blob/main/extras/bits-bytes/"


def stage():
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir()
    files = list((ROOT / "docs").glob("[0-9][0-9]-*.md")) + [ROOT / "docs/SUMMARY.md"]
    for source in files:
        text = source.read_text()
        if source.name == "11-project.md":
            # These four snippets are parts of one tested Cargo library.
            text = text.replace("```rust\n", "```rust,ignore,noplayground\n")
        def link(match):
            url = match[1]
            parsed = urllib.parse.urlsplit(url)
            if parsed.scheme or not parsed.path:
                return match[0]
            target = (source.parent / parsed.path).resolve()
            if target in files:
                return match[0]
            relative = target.relative_to(ROOT).as_posix()
            return "](" + REPO + relative + ("#" + parsed.fragment if parsed.fragment else "") + ")"
        text = re.sub(r"\]\(([^\s)]+)\)", link, text)
        (STAGE / source.name).write_text(text)
    print(f"Prepared {len(files)-1} chapters in .book-src/.")


if __name__ == "__main__":
    stage()
