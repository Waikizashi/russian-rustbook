#!/usr/bin/env python3
"""Build the complete Russian Rust Book from its canonical chapter sources."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import zipfile
import urllib.parse
from xml.etree import ElementTree as ET

from check_book import ast, nodes
from book_config import NAME, PUBLICATION

ROOT = Path(__file__).resolve().parents[1]


def resolve_html_links(epub, source):
    """Resolve links inside raw HTML, which Pandoc cannot rewrite across splits."""
    with zipfile.ZipFile(epub) as archive:
        entries = [(item, archive.read(item.filename)) for item in archive.infolist()]
    anchors = {}
    for item, data in entries:
        if item.filename.endswith(".xhtml"):
            for element in ET.fromstring(data).iter():
                if element.get("id"):
                    anchors[element.get("id")] = item.filename
    headers = []
    walk(source["blocks"], lambda node: headers.append(node["c"]) if node.get("t") == "Header" else None)
    def plain(value):
        if isinstance(value, dict):
            if value.get("t") == "Str": return value["c"]
            if value.get("t") == "Code": return value["c"][1]
            if value.get("t") in {"Space", "SoftBreak", "LineBreak"}: return " "
            return plain(value.get("c", []))
        if isinstance(value, list): return "".join(plain(child) for child in value)
        return ""
    with zipfile.ZipFile(epub, "w") as archive:
        for item, data in entries:
            if item.filename.endswith(".xhtml"):
                def resolve(match):
                    fragment = match[1]
                    target = anchors.get(urllib.parse.unquote(fragment))
                    if target and target != item.filename:
                        return 'href="' + posixpath.relpath(target, posixpath.dirname(item.filename)) + '#' + fragment + '"'
                    return match[0]
                data = re.sub(r'href="#([^"]+)"', resolve, data.decode("utf-8")).encode("utf-8")
            if item.filename.endswith("/nav.xhtml"):
                namespace = "http://www.w3.org/1999/xhtml"
                tag = lambda name: "{" + namespace + "}" + name
                doc = ET.fromstring(data)
                toc = next(e for e in doc.iter(tag("nav")) if e.get("{http://www.idpf.org/2007/ops}type") == "toc")
                for child in list(toc):
                    if child.tag == tag("ol"): toc.remove(child)
                listing = ET.SubElement(toc, tag("ol"))
                stack = [(0, listing, None)]
                for level, attr, text in headers:
                    while len(stack) > 1 and stack[-1][0] >= level: stack.pop()
                    parent = stack[-1]
                    if parent[2] is not None:
                        listing = parent[2].find(tag("ol"))
                        if listing is None: listing = ET.SubElement(parent[2], tag("ol"))
                    else: listing = parent[1]
                    entry = ET.SubElement(listing, tag("li"))
                    href = posixpath.relpath(anchors[attr[0]], posixpath.dirname(item.filename)) + "#" + attr[0]
                    ET.SubElement(entry, tag("a"), {"href": href}).text = plain(text)
                    stack.append((level, listing, entry))
                ET.register_namespace("", namespace)
                ET.register_namespace("epub", "http://www.idpf.org/2007/ops")
                data = ET.tostring(doc, encoding="utf-8", xml_declaration=True)
            elif item.filename.endswith(".ncx"):
                namespace = "http://www.daisy.org/z3986/2005/ncx/"
                tag = lambda name: "{" + namespace + "}" + name
                doc = ET.fromstring(data)
                navmap = doc.find(tag("navMap"))
                if navmap is not None:
                    navmap.clear()
                    stack = [(0, navmap)]
                    for index, (level, attr, text) in enumerate(headers, 1):
                        while len(stack) > 1 and stack[-1][0] >= level: stack.pop()
                        point = ET.SubElement(stack[-1][1], tag("navPoint"), {"id": "navPoint-"+str(index), "playOrder": str(index)})
                        ET.SubElement(ET.SubElement(point, tag("navLabel")), tag("text")).text = plain(text)
                        href = posixpath.relpath(anchors[attr[0]], posixpath.dirname(item.filename)) + "#" + attr[0]
                        ET.SubElement(point, tag("content"), {"src": href})
                        stack.append((level, point))
                    ET.register_namespace("", namespace)
                    data = ET.tostring(doc, encoding="utf-8", xml_declaration=True)
            archive.writestr(item, data)


def walk(value, fn):
    if isinstance(value, dict):
        fn(value)
        for child in list(value.values()):
            walk(child, fn)
    elif isinstance(value, list):
        for child in value:
            walk(child, fn)


def main():
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    order = json.loads((ROOT / "verification/official-order.json").read_text())
    headings = json.loads((ROOT / "verification/official-headings.json").read_text())
    upstream = json.loads((ROOT / "upstream.json").read_text())
    date = datetime.fromtimestamp(int(os.environ.get("SOURCE_DATE_EPOCH", datetime.now().timestamp())), timezone.utc).date().isoformat()
    blocks = []
    api = None
    for file in order:
        parsed = ast(ROOT / "src" / file)
        api = parsed["pandoc-api-version"]
        prefix = file[:-3] + "--"
        header_ids = {h[1] for h in headings[file]}
        header_index = [0]
        def clean(value):
            if isinstance(value, list):
                result = []
                skip_closing_anchor = None
                for child in value:
                    if isinstance(child, dict) and child.get("t") == "Span" and child["c"][0][0] in header_ids and not child["c"][1]:
                        continue
                    if skip_closing_anchor:
                        closing = skip_closing_anchor
                        skip_closing_anchor = None
                        if isinstance(child, dict) and child.get("t") == "RawInline" and child["c"] == ["html", closing]:
                            continue
                    if isinstance(child, dict) and child.get("t") == "RawBlock" and child["c"][0] == "html":
                        match = re.fullmatch(r'<a id="([^"]+)"></a>', child["c"][1].strip())
                        if match and match[1] in header_ids:
                            continue
                    if isinstance(child, dict) and child.get("t") == "RawInline" and child["c"][0] == "html":
                        match = re.fullmatch(r'<(a|span) id="([^"]+)">', child["c"][1].strip())
                        if match and match[2] in header_ids:
                            skip_closing_anchor = "</" + match[1] + ">"
                            continue
                    result.append(clean(child))
                return result
            if isinstance(value, dict):
                if value.get("t") == "Header":
                    value["c"][1][0] = headings[file][header_index[0]][1]
                    header_index[0] += 1
                for key, child in list(value.items()):
                    value[key] = clean(child)
            return value
        parsed["blocks"] = clean(parsed["blocks"])
        def resolve_url(url):
            path, sep, fragment = url.partition("#")
            target = path or file
            if target in order:
                return "#" + target[:-3] + "--" + (fragment if sep else headings[target][0][1])
            return url
        def adjust(node):
            if node.get("t") == "Header":
                node["c"][1][0] = prefix + node["c"][1][0]
            elif node.get("t") in ["RawBlock", "RawInline"] and node["c"][0] == "html":
                node["c"][1] = re.sub(r'id="([^"]+)"', lambda m: 'id="'+prefix+m[1]+'"', node["c"][1])
                node["c"][1] = re.sub(r'href="([^"]+)"', lambda m: 'href="'+resolve_url(m[1])+'"', node["c"][1])
            elif node.get("t") == "Link":
                node["c"][2][0] = resolve_url(node["c"][2][0])
        walk(parsed["blocks"], adjust)
        blocks.extend(parsed["blocks"])
    edition = f'''# Об этой русской редакции {{#edition}}

Полный русский перевод The Rust Programming Language. Авторы оригинала: Steve Klabnik, Carol Nichols, Chris Krycho и сообщество Rust. Русская основа — rust-lang-ru/book; изменённые и отсутствовавшие разделы актуализированы с помощью ChatGPT. Публикацию сопровождает Evgenii Panarin.

Дата сборки: {date}. Источники сверены {upstream['checked_at']}. Официальный commit: `{upstream['official_commit']}`. Русская основа: `{upstream['russian_commit']}`. Книга предполагает Rust {upstream['rust']} и edition {upstream['edition']}.

Это самостоятельное неофициальное издание. Основная структура, {upstream['official_headings']} заголовка и {upstream['official_code_blocks']} блоков кода и вывода проверяются автоматически. Лицензия: MIT или Apache-2.0. DRM отсутствует.

Практическое дополнение о битах и байтах доступно отдельно в [репозитории Russian Rustbook](https://github.com/Waikizashi/russian-rustbook/tree/main/extras/bits-bytes).
'''
    edition_ast = json.loads(subprocess.check_output(["pandoc", "-f", "markdown", "-t", "json"],input=edition,text=True))
    all_blocks = edition_ast["blocks"] + blocks
    license_md = "# Авторские права и лицензии {#licenses}\n\n"
    for file in ["LICENSE-MIT", "LICENSE-APACHE", "LICENSES/russian-translation-LICENSE-MIT", "LICENSES/russian-translation-LICENSE-APACHE"]:
        license_md += "\n## " + file + "\n\n" + (ROOT / file).read_text() + "\n\n"
    license_ast = json.loads(subprocess.check_output(["pandoc", "-f", "markdown", "-t", "json"],input=license_md,text=True))
    all_blocks.extend(license_ast["blocks"])
    metadata = {
        "title":{"t":"MetaString","c":PUBLICATION["title"]},
        "subtitle":{"t":"MetaString","c":PUBLICATION["subtitle"]},
        "lang":{"t":"MetaString","c":PUBLICATION["language"]},
        "date":{"t":"MetaString","c":date},
        "author":{"t":"MetaList","c":[{"t":"MetaString","c":a} for a in PUBLICATION["authors"]]},
        "toc-title":{"t":"MetaString","c":"Оглавление"},
        "rights":{"t":"MetaString","c":"MIT OR Apache-2.0. Russian translation: rust-lang-ru/book; актуализация с помощью ChatGPT."},
        "description":{"t":"MetaString","c":"Полный неофициальный русский перевод. Rust "+upstream["rust"]+", edition "+upstream["edition"]+". Официальный commit "+upstream["official_commit"]},
    }
    combined = {"pandoc-api-version":api,"meta":metadata,"blocks":all_blocks}
    source = out / "epub-source.json"
    source.write_text(json.dumps(combined,ensure_ascii=False))
    resource = str(ROOT / "src")
    subprocess.run(["pandoc",str(source),"-f","json","-t","epub3","--toc","--toc-depth=6","--split-level=1","--no-highlight","--resource-path",resource,"--css",str(ROOT/"assets/ebook.css"),"-o",str(out/(NAME+".epub"))],check=True)
    resolve_html_links(out / (NAME + ".epub"), combined)
    subprocess.run(["pandoc",str(source),"-f","json","-t","markdown","--standalone","--toc","--toc-depth=6","--wrap=none","-o",str(out/(NAME+".md"))],check=True)
    with zipfile.ZipFile(out/(NAME+"_Markdown.zip"),"w",zipfile.ZIP_DEFLATED) as z:
        z.write(out/(NAME+".md"),NAME+".md")
        for image in (ROOT/"src/img").rglob("*"):
            if image.is_file():z.write(image,str(image.relative_to(ROOT/"src")))
        for file in ["LICENSE-MIT","LICENSE-APACHE"]:z.write(ROOT/file,file)
    for extension in [".epub",".md"]:
        shutil.copyfile(out/(NAME+extension),ROOT/"downloads"/(NAME+extension))
    shutil.copyfile(out/(NAME+"_Markdown.zip"),ROOT/"downloads"/(NAME+"_Markdown.zip"))
    print("Built the complete Russian Rust Book: EPUB, Markdown and an illustrated Markdown archive.")


if __name__ == "__main__":
    main()
