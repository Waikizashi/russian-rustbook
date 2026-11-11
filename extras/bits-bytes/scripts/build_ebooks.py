#!/usr/bin/env python3
"""Export the canonical chapters to EPUB and one navigable Markdown file."""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
NAME = "Rust_Book_Bits_Bytes_RU_2026"
REPO = "https://github.com/Waikizashi/russian-rustbook/blob/main/extras/bits-bytes/"


def main():
    OUT.mkdir(exist_ok=True)
    chapters = sorted((ROOT / "docs").glob("[0-9][0-9]-*.md"))
    ids = {ident for p in chapters for ident in re.findall(r'<a id="([^"]+)"', p.read_text())}
    texts, toc = [], []
    for p in chapters:
        text = re.sub(r'<a id="([^"]+)"></a>\n\n(#{1,6}) ([^\n]+)', lambda m: m[2] + " " + m[3] + " {#" + m[1] + "}", p.read_text())
        def link(match):
            url = match[1]
            if re.match(r"(?:\d\d-[^/#]+\.md)?#", url):
                ident = url.split("#", 1)[1]
                if ident in ids:
                    return "](#" + ident + ")"
            if url.startswith("../"):
                return "](" + REPO + url[3:] + ")"
            return match[0]
        text = re.sub(r"\]\(([^\s)]+)\)", link, text)
        for level, title, ident in re.findall(r"^(#{1,2}) (.+?) \{#([^}]+)\}$", text, re.M):
            toc.append(("  " if len(level) == 2 else "") + "- [" + title + "](#" + ident + ")")
        texts.append(text)
    date = datetime.fromtimestamp(int(os.environ.get("SOURCE_DATE_EPOCH", datetime.now().timestamp())), timezone.utc).date().isoformat()
    metadata = "\n".join([
        "---", 'title: "Биты, байты и двоичные данные в Rust"',
        'subtitle: "Практическое дополнение к The Rust Programming Language"',
        'author: ["Evgenii Panarin", "Участники проекта"]',
        "lang: ru", 'date: "' + date + '"',
        'rights: "MIT. Первая редакция подготовлена с помощью ChatGPT. Самостоятельный неофициальный проект."',
        'toc-title: "Оглавление"', "---", "",
    ])
    body = "\n\n".join(texts) + "\n"
    source = OUT / "epub-source.md"
    source.write_text(metadata + body)
    (OUT / (NAME + ".md")).write_text(metadata + "\n# Оглавление\n\n" + "\n".join(toc) + "\n\n" + body)
    subprocess.run([
        "pandoc", str(source), "-f", "markdown-tex_math_dollars", "-t", "epub3",
        "--standalone", "--toc", "--toc-depth=2", "--split-level=1", "--no-highlight",
        "--css", str(ROOT / "assets/ebook.css"), "-o", str(OUT / (NAME + ".epub")),
    ], check=True)
    print("Built EPUB and Markdown in dist/.")


if __name__ == "__main__":
    main()
