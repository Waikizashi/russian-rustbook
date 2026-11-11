#!/usr/bin/env python3
"""Flag long English prose in the Russian chapters, excluding code."""
import json
import re
from check_book import ROOT, ast


def prose(node):
    if isinstance(node, dict):
        if node.get("t") in {"Code", "CodeBlock", "RawInline", "RawBlock"}:
            return ""
        if node.get("t") == "Str":
            return node["c"] + " "
        return "".join(prose(value) for value in node.values())
    if isinstance(node, list):
        return "".join(prose(value) for value in node)
    return ""


def paragraphs(node):
    if isinstance(node, dict):
        if node.get("t") in {"Para", "Plain"}:
            yield node
        for value in node.values():
            yield from paragraphs(value)
    elif isinstance(node, list):
        for value in node:
            yield from paragraphs(value)


def main():
    candidates, count = [], 0
    for file in json.loads((ROOT / "verification/official-order.json").read_text()):
        for paragraph in paragraphs(ast(ROOT / "src" / file)["blocks"]):
            count += 1
            text = prose(paragraph)
            latin = len(re.findall(r"[A-Za-z]{2,}", text))
            russian = len(re.findall(r"[А-Яа-яЁё]{2,}", text))
            if latin >= 40 and russian < latin * .1:
                candidates.append({"file": file, "latin_words": latin, "russian_words": russian, "excerpt": text[:250]})
    report = {"paragraphs_checked": count, "long_english_prose_candidates": candidates,
              "rule": "At least 40 Latin words and fewer than 10% Cyrillic words; excludes code and raw HTML. This heuristic does not replace editorial review."}
    (ROOT / "verification/language-scan.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))
    assert not candidates, "Review the English prose candidates"


if __name__ == "__main__":
    main()
