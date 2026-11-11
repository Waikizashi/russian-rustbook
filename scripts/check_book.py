#!/usr/bin/env python3
"""Verify official chapter order, headings, code, and local book links."""
from pathlib import Path
import argparse
import json
import re
import subprocess
import urllib.parse
from official import digest, summary_structure

ROOT = Path(__file__).resolve().parents[1]


def ast(file):
    return json.loads(subprocess.check_output(["pandoc", "-f", "gfm", "-t", "json", str(file)]))


def nodes(value, kind):
    result = []
    if isinstance(value, dict):
        if value.get("t") == kind:
            result.append(value)
        for child in value.values():
            result.extend(nodes(child, kind))
    elif isinstance(value, list):
        for child in value:
            result.extend(nodes(child, kind))
    return result


def validate(reference=None):
    reference = reference.resolve() if reference else ROOT
    metadata = json.loads((reference / "upstream.json").read_text())
    order = json.loads((reference / "verification/official-order.json").read_text())
    expected = json.loads((reference / "verification/official-code.json").read_text())
    headings = json.loads((reference / "verification/official-headings.json").read_text())
    manifest = json.loads((reference / "upstream/manifest.json").read_text())
    state = json.loads((reference / "translation-state.json").read_text())
    assert manifest["commit"] == metadata["official_commit"], "Manifest and lock commits differ"
    assert set(state["chapters"]) == set(order), "Translation ledger does not cover every official chapter"
    for file in order:
        assert state["chapters"][file].get("source_sha256") == manifest["chapters"][file]["source_sha256"], (file, "Upstream changes have not been reviewed")
        chapter = manifest["chapters"][file]
        original = (reference / "upstream/en" / file).read_text()
        assert digest(original.encode()) == chapter["markdown_sha256"], (file, "Stored English source differs from the manifest")
        assert digest({"markdown": original, "dependencies": chapter["dependencies"]}) == chapter["source_sha256"], (file, "Invalid source fingerprint")
        assert digest([code.rstrip("\n") for code in expected[file]]) == chapter["code_sha256"], (file, "Reference code differs from the upstream manifest")
        assert (ROOT / "src" / file).is_file(), (file, "Missing Russian chapter")
    summary = (ROOT / "src/SUMMARY.md").read_text()
    actual_order = [p for p in re.findall(r"\]\(([^)]+)\)", summary) if p in order]
    assert actual_order == order, "Official order differs"
    assert [entry for entry in summary_structure(summary) if entry[2] in order] == manifest["structure"], "Official chapter nesting differs"
    for image, expected_sha in manifest["images"].items():
        path = (reference / "images" / image) if reference != ROOT else (ROOT / "src" / image)
        assert digest(path.read_bytes()) == expected_sha, (image, "Image differs from the official snapshot")
    anchors = {f:set(re.findall(r'id="([^"]+)"', (ROOT / "src" / f).read_text())) for f in order}
    broken, references, code_count, heading_count = [], 0, 0, 0
    for f in order:
        path = ROOT / "src" / f
        text = path.read_text()
        parsed = ast(path)
        code = [b["c"][1] for b in nodes(parsed["blocks"], "CodeBlock")]
        # Fence serialization may normalize the terminal line ending.
        assert [c.rstrip("\n") for c in code] == [c.rstrip("\n") for c in expected[f]], (f, "Code/output differs from official source")
        found = nodes(parsed["blocks"], "Header")
        assert [h["c"][0] for h in found] == [h[0] for h in headings[f]], (f, "Heading levels differ")
        ids = re.findall(r'<a id="([^"]+)"></a>', text)
        position = -1
        for _, ident, _ in headings[f]:
            index = ids.index(ident)
            assert index > position, (f, ident, "Anchor order differs")
            position = index
        assert "{{#" not in text, (f, "Unexpanded include")
        code_count += len(code)
        heading_count += len(found)
        for item in nodes(parsed["blocks"], "Link") + nodes(parsed["blocks"], "Image"):
            url = item["c"][2][0]
            split = urllib.parse.urlsplit(url)
            if split.scheme or url.startswith("//"):
                continue
            references += 1
            target = (path.parent / urllib.parse.unquote(split.path)).resolve() if split.path else path
            if reference != ROOT and target.is_relative_to(ROOT / "src"):
                asset = reference / "images" / target.relative_to(ROOT / "src")
                if asset.is_file(): target = asset
            if not target.exists():
                broken.append((f, url))
            elif split.fragment and target.name in anchors and urllib.parse.unquote(split.fragment) not in anchors[target.name]:
                broken.append((f, url))
    assert not broken, broken
    assert (len(order), heading_count, code_count) == (metadata["official_files"], metadata["official_headings"], metadata["official_code_blocks"])
    print(json.dumps({"official_files":len(order),"headings":heading_count,"code_blocks":code_count,"local_references":references,"broken_links":0},ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, help="Validate Russian chapters against a prepared upstream update")
    args = parser.parse_args()
    validate(args.candidate)


if __name__ == "__main__":
    main()
