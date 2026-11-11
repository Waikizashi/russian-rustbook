"""Read official mdBook sources and resolve their visible code listings.

The listing normalization follows the conversion used for the initial edition.
Only the Python standard library and Pandoc are required.
"""
from pathlib import Path
import hashlib
import html
import json
import re
import subprocess


def digest(data):
    if not isinstance(data, bytes):
        data = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()


def summary_structure(text):
    return [[len(indent.expandtabs(4)), bool(bullet), file] for indent, bullet, file in
            re.findall(r"^([ \t]*)([-*+][ \t]+)?\[[^\]]+\]\(([^)]+\.md)\)", text, re.M)]


def preprocess(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    def listing(match):
        attrs = {key: html.unescape(a or b) for key, a, b in re.findall(r'''([\w-]+)=(?:"([^"]*)"|'([^']*)')''', match[1])}
        return ("\n\n" + ("File: `" + attrs["file-name"] + "`\n\n" if "file-name" in attrs else "")
                + match[2] + "\n\n" + ("Listing " + attrs["number"] + ": " if "number" in attrs else "") + attrs.get("caption", "") + "\n\n")
    text = re.sub(r'''<Listing\b((?:"[^"]*"|'[^']*'|[^"'>])*)>(.*?)</Listing>''', listing, text, flags=re.S)
    text = re.sub(r'<span class="(?:caption|filename)">(.*?)</span>', lambda m: "\n\n" + m[1] + "\n\n", text, flags=re.S)
    text = re.sub(r"<figcaption>(.*?)</figcaption>", lambda m: "\n\n" + m[1] + "\n\n", text, flags=re.S)
    def image(match):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', match[1]))
        return "\n\n![" + attrs.get("alt", "") + "](" + attrs["src"] + ")\n\n"
    text = re.sub(r"<img\b([^>]*)/?>", image, text, flags=re.S)
    text = re.sub(r"</?(?:figure|section|aside|div|Note)\b[^>]*>", "\n\n", text)
    text = re.sub(r"<code>(.*?)</code>", r"`\1`", text, flags=re.S)
    text = re.sub(r"</?(?:em|i)>", "*", text)
    return re.sub(r"</?(?:strong|b)>", "**", text)


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def plain(value):
    if isinstance(value, list): return "".join(plain(child) for child in value)
    if not isinstance(value, dict): return ""
    kind, content = value.get("t"), value.get("c")
    if kind == "Str": return content
    if kind == "RawInline": return content[1]
    if kind in {"Space", "SoftBreak", "LineBreak"}: return " "
    if kind == "Code": return content[1]
    if kind in {"Link", "Image"}: return plain(content[1])
    return plain(content)


def visible_code(code, language, source, dependencies):
    def include(match):
        spec = match[2].strip().split(":")
        path = (source / spec[0]).resolve()
        relative = path.relative_to(source.parent.resolve()).as_posix()
        data = path.read_bytes()
        dependencies[relative] = digest(data)
        lines = data.decode("utf-8").splitlines()
        selection = spec[1:]
        if selection and selection[0] and not selection[0].isdigit():
            anchor, active, found, selected = selection[0], False, False, []
            for line in lines:
                if re.search(r"ANCHOR:\s*" + re.escape(anchor) + r"\s*$", line):
                    active, found = True, True
                    continue
                if re.search(r"ANCHOR_END:\s*" + re.escape(anchor) + r"\s*$", line):
                    active = False
                    continue
                if active: selected.append(line)
            if not found: raise ValueError(f"Missing include anchor {anchor}: {path}")
            lines = selected
        elif selection:
            start = int(selection[0] or "1") - 1
            end = int(selection[1]) if len(selection) > 1 and selection[1] else (len(lines) if len(selection) > 1 else start + 1)
            lines = lines[start:end]
        lines = [line for line in lines if not re.search(r"ANCHOR(?:_END)?:", line)]
        if match[1] == "rustdoc_include":
            lines = [line[1:] if line.startswith("##") else line for line in lines if not re.match(r"^\s*#(?: |$)", line)]
        return "\n".join(lines)
    code = re.sub(r"{{#(rustdoc_include|include)\s+([^}]+)}}", include, code)
    if language.startswith("rust"):
        code = "\n".join(line[1:] if line.startswith("##") else line for line in code.split("\n") if not re.match(r"^\s*#(?: |$)", line))
    if "{{#" in code: raise ValueError("Unsupported mdBook macro in code; update the source adapter")
    return code


def snapshot(repository, commit):
    source = Path(repository).resolve() / "src"
    summary = (source / "SUMMARY.md").read_text()
    order = re.findall(r"\]\(([^)]+\.md)\)", summary)
    if not order or len(order) != len(set(order)): raise ValueError("Empty or duplicate official chapter paths")
    headings, code, chapters, originals, images = {}, {}, {}, {}, set()
    for file in order:
        path = (source / file).resolve()
        path.relative_to(source)
        raw = path.read_text()
        originals[file] = raw
        parsed = json.loads(subprocess.check_output(["pandoc", "-f", "markdown+raw_html-implicit_figures-tex_math_dollars", "-t", "json"], input=preprocess(raw), text=True))
        dependencies, visible = {}, []
        nodes = list(walk(parsed["blocks"]))
        for node in nodes:
            if node.get("t") == "CodeBlock":
                attrs, text = node["c"]
                visible.append(visible_code(text, attrs[1][0] if attrs[1] else "", source, dependencies))
            elif node.get("t") == "Image":
                image = node["c"][2][0]
                if re.match(r"\w+:", image): continue
                image_path = (source / image).resolve()
                image_path.relative_to(source)
                dependencies["src/" + image] = digest(image_path.read_bytes())
                images.add(image)
        # Keep AST semantics for prose, but compare code separately.
        prose = json.loads(json.dumps(parsed["blocks"]))
        for node in walk(prose):
            if node.get("t") == "CodeBlock": node["c"][1] = ""
        headings[file] = [[n["c"][0], n["c"][1][0], plain(n["c"][2])] for n in nodes if n.get("t") == "Header"]
        code[file] = visible
        chapters[file] = {"source_sha256": digest({"markdown": raw, "dependencies": dependencies}),
                          "markdown_sha256": digest(raw.encode()), "prose_sha256": digest(prose),
                          "code_sha256": digest([item.rstrip("\n") for item in visible]),
                          "dependencies": dependencies, "headings": len(headings[file]), "code_blocks": len(visible)}
    title = originals[order[0]]
    rust = re.search(r"Rust (\d+\.\d+\.\d+)", title)
    edition = re.search(r'edition\s*=\s*"(20\d\d)"', title)
    if not rust or not edition: raise ValueError("Cannot identify Rust version/edition: review title-page parser")
    return {"schema_version": 1, "commit": commit, "summary_sha256": digest(summary.encode()), "structure": summary_structure(summary),
            "images": {image: digest((source / image).read_bytes()) for image in sorted(images)},
            "rust": rust[1], "edition": edition[1], "chapters": chapters}, order, headings, code, originals, summary, sorted(images)
