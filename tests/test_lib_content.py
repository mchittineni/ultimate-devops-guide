"""Unit tests for the shared frontmatter parser and index helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from lib_content import normalize_markdown, parse_frontmatter, replace_block

QUESTION = """---
title: "What is a Pod?"
id: 12
difficulty: Beginner
tags:
  - devops
  - kubernetes
quiz:
  stem: "Which statement is true?"
  options:
    - "A"
    - "B"
  answer: 2
---

# What is a Pod?
"""


class ParseFrontmatterTests(unittest.TestCase):
    def test_scalars_lists_and_nested_quiz(self):
        meta, body = parse_frontmatter(QUESTION)
        self.assertEqual(meta["title"], "What is a Pod?")
        self.assertEqual(meta["id"], "12")
        self.assertEqual(meta["tags"], ["devops", "kubernetes"])
        self.assertEqual(meta["quiz"]["options"], ["A", "B"])
        self.assertEqual(meta["quiz"]["answer"], "2")
        self.assertTrue(body.lstrip().startswith("# What is a Pod?"))

    def test_missing_frontmatter_returns_body_unchanged(self):
        meta, body = parse_frontmatter("# No frontmatter\n")
        self.assertEqual(meta, {})
        self.assertEqual(body, "# No frontmatter\n")

    def test_empty_list_key(self):
        meta, _ = parse_frontmatter("---\ntitle: x\ntags:\n---\n")
        self.assertEqual(meta["tags"], [])

    def test_comments_are_ignored(self):
        meta, _ = parse_frontmatter("---\n# a comment\ntitle: x\n---\n")
        self.assertEqual(meta, {"title": "x"})


class ReplaceBlockTests(unittest.TestCase):
    def test_replaces_only_marker_content(self):
        text = "before\n<!-- X:START -->\nold\n<!-- X:END -->\nafter"
        out = replace_block(text, "X", "new")
        self.assertEqual(out, "before\n<!-- X:START -->\n\nnew\n\n<!-- X:END -->\nafter")

    def test_is_idempotent(self):
        text = "<!-- X:START -->\nold\n<!-- X:END -->"
        once = replace_block(text, "X", "new")
        self.assertEqual(replace_block(once, "X", "new"), once)

    def test_missing_marker_fails_loudly(self):
        with self.assertRaises(SystemExit):
            replace_block("no markers here", "X", "new")


class NormalizeMarkdownTests(unittest.TestCase):
    def test_prettier_table_padding_is_ignored(self):
        compact = "| a | b |\n| --- | --- |\n| 1 | 2 |"
        padded = "| a   | b   |\n| --- | ------ |\n|  1  |  2  |"
        self.assertEqual(normalize_markdown(compact), normalize_markdown(padded))

    def test_real_content_change_is_detected(self):
        self.assertNotEqual(normalize_markdown("| a |"), normalize_markdown("| b |"))


if __name__ == "__main__":
    unittest.main()
