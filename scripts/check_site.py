#!/usr/bin/env python3
"""Validate HTML/CSS resources, local links and fragments at the Pages base path."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
from urllib.parse import unquote, urljoin, urlsplit

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
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])
        for key in ("href", "src", "poster"):
            if attrs.get(key):
                self.urls.append(attrs[key])
        if attrs.get("srcset"):
            self.urls.extend(x.strip().split()[0] for x in attrs["srcset"].split(",") if x.strip())


def resolve_url(path, url, directory, base):
    page_url = base + path.relative_to(directory).as_posix()
    split = urlsplit(urljoin(page_url, url))
    origin = urlsplit(base)
    if split.scheme not in {"http", "https"} or split.netloc != origin.netloc:
        return None
    if not split.path.startswith(origin.path):
        raise ValueError("same-host URL escapes the project base path")
    target = (directory / unquote(split.path[len(origin.path):])).resolve()
    if not target.is_relative_to(directory):
        raise ValueError("path escapes site output")
    if target.is_dir():
        target /= "index.html"
    return target, unquote(split.fragment)


def main():
    directory = (ROOT / "book").resolve()
    base = json.loads((ROOT / "config/seo.json").read_text())["base_url"]
    pages = {path: Page(path.read_text()) for path in directory.rglob("*.html")}
    if not pages:
        raise SystemExit("No HTML files; build the site first")
    sources = {p: page.urls for p, page in pages.items()}
    sources.update({p: re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)', p.read_text()) for p in directory.rglob("*.css")})
    broken, references = [], 0
    for path, urls in sources.items():
        for url in urls:
            try:
                resolved = resolve_url(path, url, directory, base)
                if resolved is None:
                    continue
                target, fragment = resolved
                references += 1
                if not target.is_file() or (fragment and target in pages and fragment not in pages[target].ids):
                    broken.append([str(path.relative_to(directory)), url])
            except ValueError as error:
                broken.append([str(path.relative_to(directory)), url, str(error)])
    report = {"html_files": len(pages), "local_references": references, "broken_links": broken}
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist/site-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))
    if broken:
        raise SystemExit("Generated site has broken links")


if __name__ == "__main__":
    main()
