#!/usr/bin/env python3
"""Validate the EPUB container, XML, navigation, links, and exact code text."""
from pathlib import Path
import hashlib
import json
import posixpath
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from book_config import NAME, PUBLICATION

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
NS = {"x":"http://www.w3.org/1999/xhtml", "o":"http://www.idpf.org/2007/opf", "d":"http://purl.org/dc/elements/1.1/"}


def find_blocks(value, kind):
    result = []
    if isinstance(value, dict):
        if value.get("t") == kind:
            result.append(value)
        for child in value.values():
            result.extend(find_blocks(child, kind))
    elif isinstance(value, list):
        for child in value:
            result.extend(find_blocks(child, kind))
    return result


def main():
    epub = OUT / (NAME + ".epub")
    ast = json.loads((OUT / "epub-source.json").read_text())
    expected_code = [b["c"][1].rstrip("\n") for b in find_blocks(ast["blocks"], "CodeBlock")]
    expected_headers = [(b["c"][0], b["c"][1][0]) for b in find_blocks(ast["blocks"], "Header")]
    with zipfile.ZipFile(epub) as z:
        assert z.testzip() is None
        assert z.infolist()[0].filename == "mimetype"
        assert z.infolist()[0].compress_type == zipfile.ZIP_STORED
        assert z.read("mimetype") == b"application/epub+zip"
        names = set(z.namelist())
        xml = {n:ET.fromstring(z.read(n)) for n in names if n.endswith((".xml", ".opf", ".ncx", ".xhtml", ".svg"))}
        opf_name = next(e.get("full-path") for e in xml["META-INF/container.xml"].iter() if e.tag.endswith("rootfile"))
        opf = xml[opf_name]
        base = posixpath.dirname(opf_name)
        items = {e.get("id"):e for e in opf.findall("o:manifest/o:item",NS)}
        assert opf.find("o:metadata/d:language",NS).text == PUBLICATION["language"]
        for item in items.values():
            assert posixpath.normpath(posixpath.join(base,item.get("href"))) in names
        code, headers = [], []
        valid_ids = {n:{e.get("id") for e in doc.iter() if e.get("id")} for n,doc in xml.items()}
        for ref in opf.findall("o:spine/o:itemref",NS):
            name = posixpath.normpath(posixpath.join(base,items[ref.get("idref")].get("href")))
            doc = xml[name]
            parents = {child:parent for parent in doc.iter() for child in parent}
            code.extend("".join(e.itertext()).rstrip("\n") for e in doc.findall(".//x:pre/x:code",NS))
            for e in doc.iter():
                tag = e.tag.rsplit("}",1)[-1]
                if tag in {"h1","h2","h3","h4","h5","h6"}:
                    ident = e.get("id") or parents[e].get("id")
                    if ident in {i for _,i in expected_headers}:
                        headers.append((int(tag[1]),ident))
        assert code == expected_code, "Code differs from the manuscript"
        assert headers == expected_headers, "Headings or order differ"
        navigation = next(item for item in items.values() if "nav" in item.get("properties", "").split())
        nav_name = posixpath.normpath(posixpath.join(base, navigation.get("href")))
        toc = next(e for e in xml[nav_name].iter() if e.get("{http://www.idpf.org/2007/ops}type") == "toc")
        nav_ids = [urllib.parse.unquote(urllib.parse.urlsplit(e.get("href")).fragment) for e in toc.findall(".//x:a", NS)]
        assert nav_ids == [ident for _, ident in expected_headers], "Navigation omits or reorders headings"
        refs = 0
        for name, doc in xml.items():
            identifiers = [e.get("id") for e in doc.iter() if e.get("id")]
            assert len(identifiers) == len(set(identifiers)), name
            for e in doc.iter():
                for attr in ("href","src"):
                    url = e.get(attr)
                    if not url or urllib.parse.urlsplit(url).scheme:
                        continue
                    split = urllib.parse.urlsplit(url)
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(name),urllib.parse.unquote(split.path))) if split.path else name
                    refs += 1
                    assert target in names, (name,url)
                    if split.fragment:
                        assert urllib.parse.unquote(split.fragment) in valid_ids[target], (name,url)
        assert "META-INF/encryption.xml" not in names
    report = {"headings":len(headers),"toc_entries":len(nav_ids),"code_blocks":len(code),"internal_references":refs,"broken_references":0,"checks":"passed","sha256":hashlib.sha256(epub.read_bytes()).hexdigest()}
    (OUT / "verification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False))


if __name__ == "__main__":
    main()
