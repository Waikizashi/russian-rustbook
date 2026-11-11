#!/usr/bin/env python3
"""Report a newer official commit without changing the Russian translation."""
from pathlib import Path
import argparse
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="Prepare a chapter-level update report when HEAD changes")
    parser.add_argument("--output", type=Path, default=ROOT / "dist/upstream-update")
    args = parser.parse_args()
    upstream = json.loads((ROOT / "upstream.json").read_text())
    current = subprocess.check_output(["git","ls-remote",upstream["official_repository"]+".git","HEAD"],text=True).split()[0]
    known = upstream["official_commit"]
    text = "# Сверка официальной книги\n\nЗафиксировано: `"+known+"`.\n\nТекущий HEAD: `"+current+"`.\n\n"
    if known == current:
        text += "Commit совпадает с исходником текущей русской редакции.\n"
    else:
        text += "Есть новая версия оригинала. Нужна содержательная сверка перевода: https://github.com/rust-lang/book/compare/"+known+"..."+current+"\n"
        if args.prepare:
            subprocess.run(["python3", str(ROOT / "scripts/upstream.py"), "prepare", "--ref", current, "--output", str(args.output)], check=True)
            text += "\n" + (args.output / "REPORT.md").read_text()
    (ROOT/"upstream-status.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
