"""Update workflow regression tests: real source/dependency changes, no network."""
from pathlib import Path
import contextlib
import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_book
import upstream
from official import snapshot, visible_code


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.source = Path(self.temporary.name) / "official"
        (self.source / "src").mkdir(parents=True)
        (self.source / "listings").mkdir()
        (self.source / "src/SUMMARY.md").write_text("[Book](title-page.md)\n- [Basics](basics.md)\n")
        (self.source / "src/title-page.md").write_text('# Book\n\nRust 1.99.1, `edition = "2024"`.\n')
        (self.source / "src/basics.md").write_text('# Basics\n\nAn explanation.\n\n```rust\n{{#rustdoc_include ../listings/main.rs:sample}}\n```\n')
        (self.source / "listings/main.rs").write_text('// ANCHOR: sample\n# fn main() {\nlet x = 1;\n# }\n// ANCHOR_END: sample\n')
        self.root.mkdir()
        upstream.write(self.root / "upstream.json", {"official_commit": "a"*40, "official_repository": "https://github.com/rust-lang/book"})
        self.patch = patch.object(upstream, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        manifest, order, headings, code = upstream.save_snapshot(self.root, self.source, "a"*40)
        (self.root / "src").mkdir()
        (self.root / "src/SUMMARY.md").write_text("[Книга](title-page.md)\n- [Основы](basics.md)\n")
        (self.root / "src/title-page.md").write_text('<a id="book"></a>\n\n# Книга\n\nРусский текст.\n')
        (self.root / "src/basics.md").write_text('<a id="basics"></a>\n\n# Основы\n\nРусский текст.\n\n```rust\nlet x = 1;\n```\n')
        upstream.write(self.root / "translation-state.json", {"schema_version": 1, "chapters": {file: {"source_sha256": manifest["chapters"][file]["source_sha256"], "reviewed_commit": "a"*40} for file in order}})

    def prepare(self, name):
        destination = self.root / name
        with contextlib.redirect_stdout(io.StringIO()):
            upstream.prepare(destination, "HEAD", self.source, "b"*40)
        return destination, upstream.read(destination / "plan.json")

    def test_identical_sources_need_no_translation_review(self):
        destination, plan = self.prepare("same")
        self.assertEqual(plan["changes"], [])
        self.assertFalse(plan["order_changed"])
        with self.assertRaises(ValueError): self.prepare("same")

    def test_included_code_change_is_detected_without_markdown_change(self):
        path = self.source / "listings/main.rs"
        path.write_text(path.read_text().replace("x = 1", "x = 2"))
        before = (self.root / "src/basics.md").read_bytes()
        destination, plan = self.prepare("code")
        self.assertEqual(len(plan["changes"]), 1)
        change = plan["changes"][0]
        self.assertEqual(change["file"], "basics.md")
        self.assertTrue(change["code_changed"])
        self.assertFalse(change["prose_changed"])
        self.assertEqual(change["dependencies"], ["listings/main.rs"])
        self.assertEqual((self.root / "src/basics.md").read_bytes(), before)
        with patch.object(check_book, "ROOT", self.root), patch.object(sys, "argv", ["check_book.py", "--candidate", str(destination)]):
            with self.assertRaisesRegex(AssertionError, "not been reviewed"): check_book.main()
        with self.assertRaisesRegex(ValueError, "code differs"): upstream.review(destination, ["basics.md"])
        chapter = self.root / "src/basics.md"
        chapter.write_text(chapter.read_text().replace("x = 1", "x = 2"))
        upstream.review(destination, ["basics.md"])
        with patch.object(check_book, "ROOT", self.root), patch.object(sys, "argv", ["check_book.py", "--candidate", str(destination)]):
            check_book.main()

    def test_added_removed_and_reordered_chapters(self):
        (self.source / "src/next.md").write_text("# Next\n\nA new chapter.\n")
        (self.source / "src/SUMMARY.md").write_text("[Book](title-page.md)\n- [Next](next.md)\n")
        destination, plan = self.prepare("structure")
        self.assertEqual(plan["removed"], ["basics.md"])
        self.assertTrue(plan["order_changed"])
        self.assertEqual(plan["changes"][0]["status"], "added")
        self.assertIn("TODO: перевести", (destination / "SUMMARY.template.md").read_text())
        self.assertFalse((self.root / "src/next.md").exists())

    def test_missing_include_anchor_fails_loudly(self):
        with self.assertRaisesRegex(ValueError, "Missing include anchor"):
            visible_code("{{#include ../listings/main.rs:missing}}", "rust", self.source / "src", {})

    def test_image_change_is_detected_without_text_or_code_change(self):
        (self.source / "src/img").mkdir()
        image = self.source / "src/img/diagram.svg"
        image.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>one</text></svg>')
        chapter = self.source / "src/basics.md"
        chapter.write_text(chapter.read_text() + '\n![Diagram](img/diagram.svg)\n')
        manifest, *_ = upstream.save_snapshot(self.root, self.source, "a"*40)
        state = upstream.read(self.root / "translation-state.json")
        for file, item in state["chapters"].items(): item["source_sha256"] = manifest["chapters"][file]["source_sha256"]
        upstream.write(self.root / "translation-state.json", state)
        image.write_text(image.read_text().replace('one', 'two'))
        _, plan = self.prepare("image")
        self.assertEqual(plan["changes"][0]["dependencies"], ["src/img/diagram.svg"])
        self.assertFalse(plan["changes"][0]["prose_changed"])
        self.assertFalse(plan["changes"][0]["code_changed"])

    def test_accept_keeps_russian_text_and_rejects_stale_plan(self):
        path = self.source / "src/basics.md"
        path.write_text(path.read_text().replace("An explanation.", "An improved explanation."))
        destination, plan = self.prepare("prose")
        before = (self.root / "src/basics.md").read_bytes()
        with patch.object(check_book, "ROOT", self.root):
            with self.assertRaisesRegex(AssertionError, "not been reviewed"): upstream.accept(destination)
            upstream.review(destination, ["basics.md"])
            upstream.accept(destination)
            self.assertEqual(upstream.read(self.root / "upstream.json")["official_commit"], "b"*40)
            self.assertEqual((self.root / "src/basics.md").read_bytes(), before)
            with self.assertRaisesRegex(ValueError, "Stale update plan"): upstream.accept(destination)


if __name__ == "__main__":
    unittest.main()
