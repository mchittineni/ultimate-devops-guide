"""Tests for the index, knowledge-graph and quiz-feed generators.

The rendering tests use small in-memory fixtures; the last class runs each generator's
``--check`` mode against the real repository, so CI fails if committed output drifts.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import ClassVar

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_knowledge_graph import embed_json, render_html
from generate_indexes import render_badges, render_headline
from lib_content import Question, Topic
from validate_content import slugify


def make_topics() -> list[Topic]:
    topic = Topic(directory="kubernetes", title="Kubernetes", order=1)
    for n, level in enumerate(("Beginner", "Intermediate", "Advanced"), start=1):
        topic.questions.append(
            Question(
                path=REPO_ROOT / "kubernetes" / f"q{n}.md",
                slug=f"q{n}",
                title=f"Q{n}",
                id=n,
                category="Kubernetes",
                difficulty=level,
            )
        )
    return [topic]


class SlugifyTests(unittest.TestCase):
    def test_contributing_rules(self):
        self.assertEqual(slugify("What is Kubernetes?"), "what-is-kubernetes")
        self.assertEqual(slugify("CI & CD"), "ci-and-cd")
        self.assertEqual(slugify("  Docker -- vs  Podman!  "), "docker-vs-podman")


class IndexRenderingTests(unittest.TestCase):
    def test_headline_uses_live_counts(self):
        self.assertIn("**3 questions across 1 topics", render_headline(make_topics()))

    def test_badges_use_live_counts(self):
        badges = render_badges(make_topics())
        self.assertIn("questions-3-blue", badges)
        self.assertIn("topics-1-blueviolet", badges)
        self.assertIn("🟢%201%20·%20🟡%201%20·%20🔴%201", badges)


class KnowledgeGraphRenderingTests(unittest.TestCase):
    GRAPH: ClassVar[dict] = {
        "nodes": [
            {"id": "topic:k8s", "type": "topic", "label": "Kubernetes"},
            {"id": "q:1", "type": "question", "label": "Why </script><b>?"},
            {"id": "q:2", "type": "question", "label": "Tom & Jerry"},
        ],
        "links": [],
    }

    def test_embedded_json_cannot_break_out_of_script(self):
        text = embed_json(self.GRAPH)
        self.assertNotIn("</script>", text)
        self.assertNotIn("<", text)
        self.assertEqual(json.loads(text), self.GRAPH)

    def test_html_reports_live_counts_and_has_no_unfilled_fields(self):
        html = render_html(self.GRAPH)
        self.assertIn("linking 2 DevOps interview questions", html)
        self.assertIn("TOPICS: <strong>1</strong>", html)
        self.assertIn('<meta name="description" content="Interactive 3D map of 2', html)
        self.assertIsNone(re.search(r"\{(question_count|topic_count|description|site_url|graph_json)\}", html))

    def test_page_has_accessibility_and_fallback_hooks(self):
        html = render_html(self.GRAPH)
        self.assertIn('<html lang="en">', html)
        self.assertIn('aria-label="Filter questions or topics"', html)
        self.assertIn('id="graph-fallback"', html)
        self.assertIn("<noscript>", html)
        self.assertIn('integrity="sha384-', html)


class CommittedOutputIsFreshTests(unittest.TestCase):
    """Each generator's --check mode must pass against the committed files."""

    def run_check(self, script: str, *args: str) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_indexes(self):
        self.run_check("generate_indexes.py", "--check")

    def test_knowledge_graph(self):
        self.run_check("build_knowledge_graph.py", "--check")

    def test_quiz_feed(self):
        self.run_check("build_quiz_data.py", "--check", "--quiet")

    def test_content_validation(self):
        self.run_check("validate_content.py", "--quiet")


if __name__ == "__main__":
    unittest.main()
