"""Unit tests for the translation pipeline's masking and link rewriting.

These run without the Anthropic SDK or an API key: only the pure helpers are imported.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from translate_lessons import check_placeholders, mask, rewrite_links, strip_wrapper, unmask

BODY = """Intro with a [[Kubernetes|wikilink]].

```yaml
apiVersion: v1
kind: Pod
```

- Item
  ```bash
  kubectl get pods
  ```

Outro."""


class MaskTests(unittest.TestCase):
    def test_round_trip_restores_original(self):
        masked, saved = mask(BODY)
        self.assertNotIn("apiVersion", masked)
        self.assertNotIn("[[", masked)
        self.assertEqual(unmask(masked, saved), BODY)

    def test_indented_fence_keeps_its_indentation(self):
        masked, saved = mask(BODY)
        self.assertIn("  ⟦C1⟧", masked)
        self.assertIn("  kubectl get pods", unmask(masked, saved))

    def test_unterminated_fence_is_left_as_text(self):
        text = "before\n```bash\nnever closed"
        masked, saved = mask(text)
        self.assertEqual(saved, {})
        self.assertEqual(masked, text)


class PlaceholderCheckTests(unittest.TestCase):
    def test_identical_placeholders_pass(self):
        self.assertIsNone(check_placeholders("a ⟦C0⟧ b ⟦W1⟧", "x ⟦W1⟧ y ⟦C0⟧"))

    def test_dropped_placeholder_is_reported(self):
        self.assertIn("missing ['⟦C0⟧']", check_placeholders("⟦C0⟧ ⟦W1⟧", "⟦W1⟧"))

    def test_duplicated_placeholder_is_reported(self):
        self.assertIsNotNone(check_placeholders("⟦W0⟧", "⟦W0⟧ ⟦W0⟧"))


class RewriteLinksTests(unittest.TestCase):
    TRANSLATED = frozenset({"kubernetes/README.md", "kubernetes/what-is-a-pod.md"})

    def rewrite(self, text: str) -> str:
        return rewrite_links(
            text,
            "kubernetes/what-is-a-pod.md",
            "i18n/es/kubernetes/what-is-a-pod.md",
            self.TRANSLATED,
            "i18n/es",
        )

    def test_link_to_translated_page_stays_in_translated_tree(self):
        self.assertEqual(self.rewrite("[back](./README.md)"), "[back](./README.md)")

    def test_link_to_untranslated_file_points_at_original(self):
        self.assertEqual(self.rewrite("[c](../CONTRIBUTING.md)"), "[c](../../../CONTRIBUTING.md)")

    def test_anchor_is_preserved(self):
        self.assertEqual(self.rewrite("[t](../README.md#-all-questions)"), "[t](../../../README.md#-all-questions)")

    def test_absolute_and_anchor_links_are_untouched(self):
        for link in ("[x](https://example.com)", "[x](#section)", "[x](mailto:a@b.c)"):
            self.assertEqual(self.rewrite(link), link)


class StripWrapperTests(unittest.TestCase):
    def test_removes_markdown_fence_around_reply(self):
        self.assertEqual(strip_wrapper("```markdown\n# Hola\n```"), "# Hola")

    def test_leaves_unwrapped_reply_alone(self):
        self.assertEqual(strip_wrapper("# Hola\n"), "# Hola")


if __name__ == "__main__":
    unittest.main()
