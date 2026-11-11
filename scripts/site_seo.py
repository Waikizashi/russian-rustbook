#!/usr/bin/env python3
"""Enrich rendered mdBook HTML, without changing translated sources or anchors.

Only Python's standard library is used. Run after building BOTH books.
"""
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tomllib
from urllib.parse import quote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "book"
CONFIG = ROOT / "config/seo.json"
TECHNICAL = {"print.html", "404.html", "toc.html"}
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def plain(text):
    return re.sub(r"\s+", " ", text).strip()


class Content(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.headings, self.paragraphs, self.images = [], [], []
        self.capture = None
        self.parts = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if re.fullmatch(r"h[1-6]", tag) or tag == "p":
            self.capture, self.parts = tag, []
        if tag == "img":
            self.images.append(dict(attrs))

    def handle_data(self, text):
        if self.capture:
            self.parts.append(text)

    def handle_endtag(self, tag):
        if tag == self.capture:
            text = plain("".join(self.parts))
            if text:
                if tag == "p":
                    self.paragraphs.append(text)
                else:
                    self.headings.append((int(tag[1]), text))
            self.capture = None


def main_html(text):
    match = re.search(r"<main\b[^>]*>(.*?)</main>", text, re.S)
    if not match:
        raise ValueError("Missing main content")
    return match


def normalize_headings(text):
    # The toolbar title is navigation, not the chapter's main heading.
    text = re.sub(r'<h1 class="menu-title">(.*?)</h1>', r'<div class="menu-title">\1</div>', text, flags=re.S)
    match = main_html(text)
    headings = re.findall(r"<h([1-6])\b", match[1])
    if not headings:
        raise ValueError("Chapter has no heading")
    offset = int(headings[0]) - 1
    previous = 0
    def heading(m):
        nonlocal previous
        level = 1 if previous == 0 else min(previous + 1, max(2, int(m[1]) - offset))
        previous = level
        return f"<h{level}{m[2]}{m[3]}</h{level}>"
    body = re.sub(r"<h([1-6])(\b[^>]*>)(.*?)</h[1-6]>", heading, match[1], flags=re.S)
    return text[:match.start(1)] + body + text[match.end(1):]


def auto_description(content):
    title = content.headings[0][1]
    paragraphs = [p for p in content.paragraphs if len(p) >= 50]
    if paragraphs:
        excerpt = paragraphs[0]
    else:
        excerpt = "; ".join(h[1] for h in content.headings[1:])
    text = plain(f"{title}. {excerpt}")
    if len(text) > 180:
        text = text[:177].rsplit(" ", 1)[0].rstrip(" ,;:.—") + "…"
    return text


def settings():
    cfg = json.loads(CONFIG.read_text())
    base = urlsplit(cfg["base_url"])
    if base.scheme != "https" or not base.netloc or base.query or base.fragment or not base.path.endswith("/"):
        raise ValueError("base_url must be an absolute HTTPS URL ending in / without query/fragment")
    return cfg


def book_settings(path):
    config = ROOT / ("extras/bits-bytes/book.toml" if path.startswith("extras/bits-bytes/") else "book.toml")
    return tomllib.loads(config.read_text())["book"]


def discover():
    # mdBook's generated index is a copy of its first chapter. Discover that
    # chapter from each SUMMARY, rather than hardcoding a list of URLs.
    aliases = {}
    for folder, summary in [("", ROOT / "src/SUMMARY.md"), ("extras/bits-bytes/", ROOT / "extras/bits-bytes/docs/SUMMARY.md")]:
        first = re.search(r"\]\(([^)#]+)\.md\)", summary.read_text())
        if not first:
            raise ValueError(f"No first chapter in {summary}")
        aliases[folder + first[1] + ".html"] = folder
        aliases[folder + "index.html"] = folder
    return sorted(SITE.rglob("*.html")), aliases


def metadata(path, text, cfg, aliases):
    rel = path.relative_to(SITE).as_posix()
    technical = path.name in TECHNICAL
    canonical_path = aliases.get(rel, rel)
    canonical = cfg["base_url"] + quote(canonical_path, safe="/-._~")
    content = Content("" if technical else main_html(text)[1])
    book = book_settings(rel)
    # Overrides for the first chapter also apply to its generated index alias.
    key = next((k for k, v in aliases.items() if v == canonical_path and not k.endswith("index.html")), rel)
    override = cfg["pages"].get(key, {})
    title = override.get("title", (content.headings[0][1] if content.headings else book["title"]) + " — " + cfg["site_name"])
    desc = override.get("description", auto_description(content) if content.headings else book["description"])
    head = [f'<title>{escape(title)}</title>', f'<meta name="description" content="{escape(desc, quote=True)}">']
    if technical:
        head.append('<meta name="robots" content="noindex, follow">')
    else:
        head.append(f'<link rel="canonical" href="{escape(canonical, quote=True)}">')
        props = {"og:title": title, "og:description": desc, "og:url": canonical, "og:type": "website" if rel in aliases else "article", "og:locale": "ru_RU", "og:site_name": cfg["site_name"], "og:image": cfg["base_url"] + "assets/social-card.png", "og:image:width": "1200", "og:image:height": "630", "og:image:alt": "Russian Rust Book — книга о Rust на русском"}
        head += [f'<meta property="{k}" content="{escape(v, quote=True)}">' for k, v in props.items()]
        head += [f'<meta name="{k}" content="{escape(v, quote=True)}">' for k, v in {"twitter:card": "summary", "twitter:title": title, "twitter:description": desc, "twitter:image": cfg["base_url"] + "assets/social-card.png", "twitter:image:alt": "Russian Rust Book — книга о Rust на русском"}.items()]
        home = cfg["base_url"] + ("extras/bits-bytes/" if rel.startswith("extras/bits-bytes/") else "")
        schema = {"@context": "https://schema.org", "@graph": []}
        schema["@graph"].append({"@type": "Book" if canonical == home else "TechArticle", "@id": canonical + "#content", "url": canonical, "name": title, "description": desc, "inLanguage": "ru", "author": [{"@type": "Person" if a != "Rust Community" and a != "Участники проекта" else "Organization", "name": a} for a in book["authors"]], "license": "https://github.com/Waikizashi/russian-rustbook/blob/main/" + ("extras/bits-bytes/LICENSE" if rel.startswith("extras/") else "NOTICE.md")})
        crumbs = [{"@type": "ListItem", "position": 1, "name": cfg["site_name"], "item": cfg["base_url"]}]
        if canonical != cfg["base_url"]:
            crumbs.append({"@type": "ListItem", "position": 2, "name": title, "item": canonical})
        schema["@graph"].append({"@type": "BreadcrumbList", "itemListElement": crumbs})
        head.append('<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + '</script>')
    for provider, name in [("google", "google-site-verification"), ("bing", "msvalidate.01")]:
        token = cfg["verification"].get(provider, "")
        if token:
            head.append(f'<meta name="{name}" content="{escape(token, quote=True)}">')
    return "\n        ".join(head), None if technical or (rel in aliases and not rel.endswith("index.html")) else canonical


def build():
    cfg = settings()
    import shutil
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "assets/social-card.png", SITE / "assets/social-card.png")
    paths, aliases = discover()
    if not paths:
        raise ValueError("Build mdBook before generating SEO")
    urls = []
    for path in paths:
        text = path.read_text()
        # mdBook 0.5 includes the configured source directory in {path}.
        text = text.replace("/edit/main/extras/bits-bytes/docs/.book-src/", "/edit/main/extras/bits-bytes/docs/")
        # Use a real keyboard-operable button; retain the checkbox/label
        # fallback for readers with JavaScript disabled.
        def sidebar_button(m):
            attrs = m[1].replace(' for="mdbook-sidebar-toggle-anchor"', '')
            return '<button type="button"' + attrs + '>' + m[2] + '</button><noscript><label class="icon-button" for="mdbook-sidebar-toggle-anchor">Оглавление</label></noscript>'
        text = re.sub(r'<label([^>]*id="mdbook-sidebar-toggle"[^>]*)>(.*?)</label>', sidebar_button, text, flags=re.S)
        # Defer external scripts in their original order; content can paint
        # without waiting for syntax highlighting and the search UI.
        text = re.sub(r'<script src="([^"]+)"', r'<script defer src="\1"', text)
        text = re.sub(r'\s*<!-- NAV:START -->.*?<!-- NAV:END -->', '', text, flags=re.S)
        text = text.replace('</body>', '<!-- NAV:START --><script>\n' + (ROOT / "assets/navigation.js").read_text() + '\n</script><!-- NAV:END -->\n</body>')
        if path.name not in TECHNICAL:
            text = normalize_headings(text)
        head, canonical = metadata(path, text, cfg, aliases)
        # Own only this marked block, the default title and description.
        text = re.sub(r'\s*<!-- SEO:START -->.*?<!-- SEO:END -->', '', text, flags=re.S)
        text = re.sub(r'<title>.*?</title>\s*', '', text, flags=re.S)
        text = re.sub(r'<meta name="(?:description|robots)"[^>]*>\s*', '', text)
        text = text.replace('</head>', '<!-- SEO:START -->\n        ' + head + '\n        <!-- SEO:END -->\n    </head>')
        path.write_text(text)
        if canonical:
            urls.append(canonical)
    ET.register_namespace("", NS)
    sitemap = ET.Element(f"{{{NS}}}urlset")
    for url in sorted(set(urls)):
        ET.SubElement(ET.SubElement(sitemap, f"{{{NS}}}url"), f"{{{NS}}}loc").text = url
    ET.indent(sitemap)
    ET.ElementTree(sitemap).write(SITE / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    (SITE / "robots.txt").write_text("# Informational copy: crawlers use /robots.txt at the HOST root.\nUser-agent: *\nAllow: /\nSitemap: " + cfg["base_url"] + "sitemap.xml\n")
    (SITE / ".nojekyll").touch()
    print(f"SEO: {len(paths)} HTML pages, {len(set(urls))} canonical sitemap URLs")


if __name__ == "__main__":
    build()
