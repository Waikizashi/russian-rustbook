#!/usr/bin/env python3
"""Check actual generated HTML targets and fragment identifiers."""
from html.parser import HTMLParser
from pathlib import Path
import json
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.urls = set(), []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.urls.append(attrs[key])


def main():
    directory = ROOT / "book"
    pages = {path.resolve(): Page(path.read_text()) for path in directory.rglob("*.html")}
    broken, references = [], 0
    for path, page in pages.items():
        for url in page.urls:
            split = urlsplit(url)
            if split.scheme or split.netloc or url.startswith("/"):
                continue
            target = (path.parent / unquote(split.path)).resolve() if split.path else path
            if target.is_dir():
                target = target / "index.html"
            references += 1
            if not target.exists() or (split.fragment and target in pages and unquote(split.fragment) not in pages[target].ids):
                broken.append([str(path.relative_to(directory.resolve())), url])
    report = {"html_files": len(pages), "local_references": references, "broken_links": broken}
    (ROOT / "dist/site-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))
    assert not broken, "Generated site has broken links"


if __name__ == "__main__":
    main()
