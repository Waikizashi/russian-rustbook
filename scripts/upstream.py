#!/usr/bin/env python3
"""Prepare, review and accept official-book updates without replacing Russian prose."""
import argparse
from datetime import date
import difflib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile

from official import digest, snapshot

ROOT = Path(__file__).resolve().parents[1]


def read(path): return json.loads(path.read_text())


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def code_text(blocks):
    return "\n\n".join(f"=== Block {index} ===\n{text.rstrip(chr(10))}" for index, text in enumerate(blocks, 1)) + "\n"


def checkout(ref):
    cache = ROOT / ".cache/official-book.git"
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--bare", "--depth=1", read(ROOT / "upstream.json")["official_repository"] + ".git", str(cache)], check=True)
    subprocess.run(["git", "-C", str(cache), "fetch", "--depth=1", "origin", ref], check=True)
    commit = subprocess.check_output(["git", "-C", str(cache), "rev-parse", "FETCH_HEAD"], text=True).strip()
    temporary = tempfile.TemporaryDirectory(prefix="rust-book-upstream-")
    archive = Path(temporary.name) / "source.tar"
    subprocess.run(["git", "-C", str(cache), "archive", "-o", str(archive), commit], check=True)
    source = Path(temporary.name) / "source"
    source.mkdir()
    with tarfile.open(archive) as tar:
        tar.extractall(source, filter="data")
    return temporary, source, commit


def save_snapshot(destination, source, commit):
    manifest, order, headings, code, originals, summary, images = snapshot(source, commit)
    metadata = read(ROOT / "upstream.json")
    metadata.update(official_commit=commit, checked_at=date.today().isoformat(), rust=manifest["rust"], edition=manifest["edition"],
                    official_files=len(order), official_headings=sum(map(len, headings.values())), official_code_blocks=sum(map(len, code.values())))
    for filename, value in [("official-order.json", order), ("official-headings.json", headings), ("official-code.json", code)]:
        write(destination / "verification" / filename, value)
    write(destination / "upstream/manifest.json", manifest)
    write(destination / "upstream.json", metadata)
    for filename, text in {**originals, "SUMMARY.md": summary}.items():
        path = destination / "upstream/en" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    for image in images:
        path = destination / "images" / image
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / "src" / image, path)
    return manifest, order, headings, code


def prepare(destination, ref, source=None, commit=None):
    if destination.exists(): raise ValueError("The update directory already exists; choose a new directory to preserve review progress")
    temporary = None
    if source is None:
        temporary, source, commit = checkout(ref)
    if not commit or not re.fullmatch(r"[0-9a-f]{40}", commit): raise ValueError("An exact official commit is required")
    destination.mkdir(parents=True)
    try:
        new, order, headings, code = save_snapshot(destination, source, commit)
        old = read(ROOT / "upstream/manifest.json")
        old_code = read(ROOT / "verification/official-code.json")
        old_order = read(ROOT / "verification/official-order.json")
        state = read(ROOT / "translation-state.json")
        changes = []
        for file in order:
            previous, current = old["chapters"].get(file), new["chapters"][file]
            if previous and previous["source_sha256"] == current["source_sha256"]: continue
            dependencies = sorted(key for key in set((previous or {}).get("dependencies", {})) | set(current["dependencies"])
                                  if (previous or {}).get("dependencies", {}).get(key) != current["dependencies"].get(key))
            changes.append({"file": file, "status": "changed" if previous else "added",
                            "prose_changed": not previous or previous["prose_sha256"] != current["prose_sha256"],
                            "code_changed": not previous or previous["code_sha256"] != current["code_sha256"], "dependencies": dependencies})
            before = (ROOT / "upstream/en" / file).read_text() if previous else ""
            after = (destination / "upstream/en" / file).read_text()
            patch = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="old/"+file, tofile="new/"+file))
            path = destination / "diffs" / (file + ".diff")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(patch)
            path.with_suffix(".code.diff").write_text("".join(difflib.unified_diff(code_text(old_code.get(file, [])).splitlines(True),
                code_text(code[file]).splitlines(True), fromfile="old/code", tofile="new/code")))
            visible = destination / "code" / (file + ".txt")
            visible.parent.mkdir(parents=True, exist_ok=True)
            visible.write_text(code_text(code[file]))
        removed = [file for file in old_order if file not in order]
        state["chapters"] = {file: state["chapters"].get(file, {}) for file in order}
        write(destination / "translation-state.json", state)
        plan = {"schema_version": 1, "base_commit": old["commit"], "target_commit": commit,
                "changes": changes, "removed": removed, "order_changed": old_order != order or old["structure"] != new["structure"]}
        write(destination / "plan.json", plan)
        labels = {path: label for label, path in re.findall(r"\[([^\]]+)\]\(([^)]+\.md)\)", (ROOT / "src/SUMMARY.md").read_text())}
        summary = (destination / "upstream/en/SUMMARY.md").read_text()
        summary = re.sub(r"\[([^\]]+)\]\(([^)]+\.md)\)", lambda m: "["+labels.get(m[2], "TODO: перевести — "+m[1])+"]("+m[2]+")", summary)
        (destination / "SUMMARY.template.md").write_text(summary + "\n# Дополнения\n\n- [Биты и байты](supplement.md)\n")
        report = ["# Обновление оригинала", "", f"База: `{old['commit']}`", f"Кандидат: `{commit}`", "",
                  "| Файл | Статус | Текст/структура | Видимый код | Зависимости |", "|---|---|---|---|---|"]
        for item in changes:
            report.append(f"| {item['file']} | {item['status']} | {'изменён' if item['prose_changed'] else 'без изменений'} | {'изменён' if item['code_changed'] else 'без изменений'} | {len(item['dependencies'])} |")
        report += ["", "Удалены: " + (", ".join(removed) or "нет"), f"Изменился порядок: {'да' if plan['order_changed'] else 'нет'}.", "",
                   "Русские главы и опубликованная версия не изменены. Подробные изменения — в diffs/ и plan.json. Порядок работы — в docs/UPDATING.md."]
        (destination / "REPORT.md").write_text("\n".join(report) + "\n")
        print(f"Prepared {len(changes)} changed/added chapters, {len(removed)} removed; Russian sources unchanged: {destination}")
    finally:
        if temporary: temporary.cleanup()


def review(plan, files):
    from check_book import ast, nodes
    manifest = read(plan / "upstream/manifest.json")
    expected = read(plan / "verification/official-code.json")
    headings = read(plan / "verification/official-headings.json")
    state = read(plan / "translation-state.json")
    for file in files:
        if file not in manifest["chapters"]: raise ValueError(f"Unknown chapter: {file}")
        source = ROOT / "src" / file
        parsed = ast(source)
        actual_code = [n["c"][1].rstrip("\n") for n in nodes(parsed["blocks"], "CodeBlock")]
        if actual_code != [text.rstrip("\n") for text in expected[file]]: raise ValueError(f"Official code differs: {file}")
        if [n["c"][0] for n in nodes(parsed["blocks"], "Header")] != [h[0] for h in headings[file]]: raise ValueError(f"Heading structure differs: {file}")
        anchors = re.findall(r'<a id="([^"]+)"></a>', source.read_text())
        if [item for item in anchors if item in {h[1] for h in headings[file]}] != [h[1] for h in headings[file]]: raise ValueError(f"Heading anchors differ: {file}")
        state["chapters"][file] = {"source_sha256": manifest["chapters"][file]["source_sha256"], "reviewed_commit": manifest["commit"],
                                     "reviewed_at": date.today().isoformat(), "translation_sha256": digest(source.read_bytes())}
    write(plan / "translation-state.json", state)
    print(f"Recorded explicit translation review for {len(files)} chapters; this does not certify translation quality automatically.")


def accept(plan):
    from check_book import validate
    info = read(plan / "plan.json")
    if info["base_commit"] != read(ROOT / "upstream.json")["official_commit"]: raise ValueError("Stale update plan: the published baseline changed")
    if info["target_commit"] != read(plan / "upstream.json")["official_commit"]: raise ValueError("Candidate commit differs from the update plan")
    validate(plan)
    # Acceptance changes reference data and assets, never the Russian chapter text.
    for name in ["translation-state.json", "upstream/manifest.json", "verification/official-order.json", "verification/official-headings.json", "verification/official-code.json"]:
        shutil.copyfile(plan / name, ROOT / name)
    shutil.rmtree(ROOT / "upstream/en")
    shutil.copytree(plan / "upstream/en", ROOT / "upstream/en")
    if (plan / "images").exists(): shutil.copytree(plan / "images", ROOT / "src", dirs_exist_ok=True)
    shutil.copyfile(plan / "upstream.json", ROOT / "upstream.json")
    print("Accepted the reviewed upstream snapshot. Rebuild EPUB/PDF/site and update CHANGELOG/VALIDATION before release.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("prepare")
    command.add_argument("--ref", default="HEAD")
    command.add_argument("--output", type=Path, required=True)
    command.add_argument("--source", type=Path, help="An already checked-out official repository, for offline use")
    command.add_argument("--commit", help="Exact official commit corresponding to --source")
    command = commands.add_parser("review")
    command.add_argument("--plan", type=Path, required=True)
    command.add_argument("files", nargs="+")
    command = commands.add_parser("accept")
    command.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare": prepare(args.output.resolve(), args.ref, args.source, args.commit)
    elif args.command == "review": review(args.plan.resolve(), args.files)
    else: accept(args.plan.resolve())


if __name__ == "__main__":
    main()
