#!/usr/bin/env python3
"""Keep the tutorial listings and standalone examples in sync."""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
FENCE = re.compile(r"```rust\n(.*?)\n```", re.S)


def listings():
    result = []
    for chapter in sorted((ROOT / "docs").glob("[0-9][0-9]-*.md")):
        for index, match in enumerate(FENCE.finditer(chapter.read_text()), 1):
            if "fn main(" not in match[1]:
                continue
            name = f"lesson{chapter.name[:2]}_{index:02d}"
            result.append((chapter, name, match[1] + "\n"))
    return result


def project_sections():
    source = (ROOT / "crates/byte-note/src/lib.rs").read_text()
    return re.findall(r"// SECTION: (\w+)\n(.*?)\n// END: \1", source, re.S)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--to-docs", action="store_true", help="copy edited/formatted Rust back into the chapters")
    args = parser.parse_args()
    if args.check and args.to_docs:
        parser.error("choose either --check or --to-docs")
    if args.to_docs:
        for chapter in sorted((ROOT / "docs").glob("[0-9][0-9]-*.md")):
            count = 0
            def replace(match):
                nonlocal count
                count += 1
                if "fn main(" not in match[1]:
                    return match[0]
                file = ROOT / "examples" / f"lesson{chapter.name[:2]}_{count:02d}.rs"
                return "```rust\n" + file.read_text().rstrip("\n") + "\n```"
            chapter.write_text(FENCE.sub(replace, chapter.read_text()))
        chapter = ROOT / "docs/11-project.md"
        sections = iter(project_sections())
        def project_replace(match):
            _, code = next(sections)
            return "```rust\n" + code + "\n```"
        chapter.write_text(FENCE.sub(project_replace, chapter.read_text()))

    errors, manifest = [], []
    for chapter, name, code in listings():
        target = ROOT / "examples" / (name + ".rs")
        if args.check:
            if not target.exists() or target.read_text() != code:
                errors.append(str(target.relative_to(ROOT)))
        else:
            target.write_text(code)
        manifest.append({"name": name, "chapter": chapter.name, "example": str(target.relative_to(ROOT))})
    expected_manifest = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    manifest_path = ROOT / "scripts/examples.json"
    if args.check:
        if manifest_path.read_text() != expected_manifest:
            errors.append("scripts/examples.json")
        actual = [m[1] for m in FENCE.finditer((ROOT / "docs/11-project.md").read_text())]
        if actual != [code for _, code in project_sections()]:
            errors.append("docs/11-project.md: project listings")
    else:
        manifest_path.write_text(expected_manifest)
    if errors:
        raise SystemExit("Code differs between docs and Rust files: " + ", ".join(errors))
    print(f"Documentation and {len(manifest)} runnable examples are synchronized.")


if __name__ == "__main__":
    main()
