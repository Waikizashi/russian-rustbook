#!/usr/bin/env python3
"""Check source navigation, local links, tutorial completeness, and code drift."""
from pathlib import Path
import re
import subprocess
import sys
import urllib.parse
import zlib

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")


def strip_code(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def anchors(text):
    found = set(re.findall(r'<a\s+id="([^"]+)"', strip_code(text)))
    for heading in re.findall(r"^#{1,6} (.+)$", strip_code(text), re.M):
        heading = re.sub(r"<[^>]+>", "", heading).lower().replace(" ", "-")
        found.add(re.sub(r"[^\w\-]", "", heading))
    return found


def main():
    errors = []
    chapters = sorted((ROOT / "docs").glob("[0-9][0-9]-*.md"))
    summary = (ROOT / "docs/SUMMARY.md").read_text()
    order = [url for url in LINK.findall(summary) if re.match(r"\d\d-", url)]
    if order != [p.name for p in chapters] or len(chapters) != 14:
        errors.append("SUMMARY.md must list all 14 chapter files in order")
    checked = 0
    for file in sorted(ROOT.rglob("*.md")):
        if any(part in {"target", "book", ".book-src", ".git", "dist"} for part in file.parts):
            continue
        text = file.read_text()
        if "{{INCLUDE:" in text or "{{GOLDEN_" in text:
            errors.append(f"Unexpanded placeholder in {file}")
        for url in LINK.findall(strip_code(text)):
            parsed = urllib.parse.urlsplit(url)
            if parsed.scheme or url.startswith("//"):
                continue
            target = (file.parent / urllib.parse.unquote(parsed.path)).resolve() if parsed.path else file.resolve()
            checked += 1
            if not target.exists():
                errors.append(f"{file.relative_to(ROOT)}: missing {url}")
            elif parsed.fragment and target.suffix == ".md" and urllib.parse.unquote(parsed.fragment) not in anchors(target.read_text()):
                errors.append(f"{file.relative_to(ROOT)}: missing anchor {url}")
    prefix = bytes.fromhex("42 59 54 45 21 01 00 03 04 03 02 01 41 D0 96")
    if zlib.crc32(prefix) != 0x22F42A3A:
        errors.append("Golden CRC differs from the independent Python implementation")
    subprocess.run([sys.executable, str(ROOT / "scripts/sync_examples.py"), "--check"], check=True)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checked {len(chapters)} chapter files and {checked} local links; golden CRC verified.")


if __name__ == "__main__":
    main()
