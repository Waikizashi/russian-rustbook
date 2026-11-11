#!/usr/bin/env python3
"""Validate rendered metadata and sitemap; no network or third-party packages."""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TECHNICAL = {"404.html", "print.html", "toc.html"}


class SEO(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.lang = None
        self.meta, self.canonical, self.titles, self.schema = [], [], [], []
        self.headings, self.images, self.edit = [], [], []
        self.in_head = self.in_main = False
        self.capture = None
        self.parts = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html": self.lang = attrs.get("lang")
        if tag == "head": self.in_head = True
        if tag == "main": self.in_main = True
        if self.in_head:
            if tag == "meta": self.meta.append(attrs)
            if tag == "link" and attrs.get("rel") == "canonical": self.canonical.append(attrs.get("href"))
            if tag == "title" or (tag == "script" and attrs.get("type") == "application/ld+json"):
                self.capture, self.parts = tag, []
        if self.in_main and tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(int(tag[1]))
        if self.in_main and tag == "img": self.images.append(attrs)
        if tag == "a" and attrs.get("rel") == "edit": self.edit.append(attrs.get("href", ""))

    def handle_data(self, data):
        if self.capture: self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == self.capture:
            (self.titles if tag == "title" else self.schema).append("".join(self.parts).strip())
            self.capture = None
        if tag == "head": self.in_head = False
        if tag == "main": self.in_main = False

    def values(self, key):
        return [m.get("content", "") for m in self.meta if m.get("name", m.get("property")) == key]


def validate(directory, cfg):
    base = cfg["base_url"]
    errors, canonical_urls, titles, descriptions = [], set(), [], []
    warnings = []
    pages = list(directory.rglob("*.html"))
    def require(condition, path, message):
        if not condition: errors.append(f"{path}: {message}")
    for path in pages:
        rel = path.relative_to(directory).as_posix()
        text = path.read_text()
        page = SEO(text)
        require(page.lang == "ru", rel, "html lang must be ru")
        require(len(page.titles) == 1 and bool(page.titles[0]), rel, "expected one nonempty title")
        desc = page.values("description")
        require(len(desc) == 1 and len(desc[0]) >= 40, rel, "expected one useful description")
        require(not page.values("keywords"), rel, "meta keywords are not used")
        if path.name in TECHNICAL:
            require(page.values("robots") == ["noindex, follow"], rel, "technical page must be noindex")
            require(not page.canonical, rel, "technical page must not claim a chapter canonical")
            continue
        require(not any("noindex" in x or "none" == x for x in page.values("robots")), rel, "chapter blocks indexing")
        require(len(page.canonical) == 1, rel, "expected one canonical")
        if len(page.canonical) != 1:
            continue
        canonical = page.canonical[0]
        require(canonical.startswith(base), rel, "canonical outside configured base URL")
        parts = urlsplit(canonical)
        require(not parts.query and not parts.fragment, rel, "canonical contains query/fragment")
        canonical_rel = unquote(canonical.removeprefix(base))
        target = directory / canonical_rel
        if target.is_dir(): target /= "index.html"
        require(target.is_file(), rel, "canonical target does not exist")
        # An alias may canonicalize only to the generated index with equal main content.
        if target != path:
            import re
            content = lambda t: re.search(r"<main\b[^>]*>(.*?)</main>", t, re.S)[1].strip()
            require(target.is_file() and content(target.read_text()) == content(text), rel, "alias canonical has different content")
        else:
            canonical_urls.add(canonical)
            titles.extend(page.titles)
            descriptions.extend(desc)
        for key, value in [("og:url", canonical), ("og:locale", "ru_RU"), ("og:title", page.titles[0]), ("og:description", desc[0]), ("twitter:card", "summary"), ("twitter:title", page.titles[0]), ("twitter:description", desc[0])]:
            require(page.values(key) == [value], rel, f"invalid {key}")
        require(len(page.edit) == 1, rel, "expected one source edit link")
        for edit in page.edit:
            prefix = "https://github.com/Waikizashi/russian-rustbook/edit/main/"
            source = ROOT / unquote(edit.removeprefix(prefix))
            require(edit.startswith(prefix) and source.is_file(), rel, "edit link does not point to an existing source")
        require(page.values("og:image") == [base + "assets/social-card.png"], rel, "missing social preview")
        require(page.values("og:type") in [["article"], ["website"]], rel, "missing og:type")
        require(page.headings.count(1) == 1 and page.headings[0] == 1, rel, "chapter needs exactly one leading H1")
        require(all(b <= a + 1 for a, b in zip(page.headings, page.headings[1:])), rel, "heading level skipped")
        for img in page.images:
            require("alt" in img and bool(img["alt"].strip()), rel, "content image missing descriptive alt")
        require(len(page.schema) == 1, rel, "expected one JSON-LD block")
        for data in page.schema:
            try:
                schema = json.loads(data)
                require(schema["@context"] == "https://schema.org", rel, "unexpected JSON-LD context")
                require(schema["@graph"][0]["url"] == canonical, rel, "JSON-LD URL differs from canonical")
            except (ValueError, KeyError, IndexError, TypeError):
                errors.append(f"{rel}: invalid JSON-LD")
    for name, values in [("title", titles), ("description", descriptions)]:
        require(not [x for x, n in Counter(values).items() if n > 1], name, "duplicates across canonical pages")
    tree = ET.parse(directory / "sitemap.xml")
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    require(tree.getroot().tag == ns + "urlset", "sitemap", "invalid namespace/root")
    urls = [n.text for n in tree.findall(ns + "url/" + ns + "loc")]
    require(len(urls) == len(set(urls)), "sitemap", "duplicate URLs")
    require(set(urls) == canonical_urls, "sitemap", "does not exactly cover canonical chapters")
    require(not tree.findall(".//" + ns + "lastmod"), "sitemap", "lastmod requires trustworthy source dates")
    robots = (directory / "robots.txt").read_text()
    require("Disallow:" not in robots and "Sitemap: " + base + "sitemap.xml" in robots, "robots.txt", "unexpected crawl policy or sitemap")
    require(bool(pages), "site", "no HTML pages")
    return {"html_files": len(pages), "canonical_pages": len(canonical_urls), "sitemap_urls": len(urls), "errors": errors, "warnings": warnings}


def main():
    cfg = json.loads((ROOT / "config/seo.json").read_text())
    report = validate(ROOT / "book", cfg)
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist/seo-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))
    if report["errors"]:
        raise SystemExit("SEO validation failed")


if __name__ == "__main__":
    main()
