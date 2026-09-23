"""Shared helpers for reading the question vault.

The repository is the source of truth: every question lives in
``topic-slug/question-slug.md`` with a YAML frontmatter block carrying its ``id``.
Ordering and topic membership come from ``topic_meta.json``, not from filenames.
Indexes (topic READMEs and the root table of contents) are generated from these
files, never hand-edited, so the two can never drift apart.

Stdlib only - no third-party YAML parser is required for the small, strict
frontmatter subset used here.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

QUESTION_FILE_RE = re.compile(r"^([a-z0-9-]+)\.md$")
TOPIC_META_PATH = Path(__file__).resolve().parent / "topic_meta.json"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

DIFFICULTIES = ("Beginner", "Intermediate", "Advanced")


@dataclass
class Question:
    path: Path
    slug: str
    title: str
    id: int
    category: str
    difficulty: str
    tags: list[str] = field(default_factory=list)
    body: str = ""
    quiz: dict | None = None

    @property
    def topic_dir(self) -> str:
        return self.path.parent.name

    @property
    def filename(self) -> str:
        return self.path.name


@dataclass
class Topic:
    directory: str
    title: str
    order: int
    questions: list[Question] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return REPO_ROOT / self.directory


def topic_meta() -> dict:
    """Registry of topic directories: order, description, and study notes.

    This file - not a numeric filename prefix - defines which directories are
    topics and the order they appear in every generated index.
    """
    return json.loads(TOPIC_META_PATH.read_text(encoding="utf-8"))


def _scalar(raw: str) -> str:
    return raw.strip().strip('"')


def _parse_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[object, int]:
    """Parse the entries sitting at ``indent`` columns; return the value and next index.

    ``lines`` is the pre-filtered (indent, text) stream. A block is a list when its
    first entry starts with ``- ``, otherwise a mapping. Nested blocks recurse, which
    is what lets the ``quiz:`` frontmatter block hold its own keys and options list.
    """
    if lines[index][1].startswith("- "):
        items: list[str] = []
        while index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("- "):
            items.append(_scalar(lines[index][1][2:]))
            index += 1
        return items, index

    mapping: dict = {}
    while index < len(lines) and lines[index][0] == indent and not lines[index][1].startswith("- "):
        key, sep, value = lines[index][1].partition(":")
        index += 1
        if not sep:
            continue  # not a key line - ignore rather than guess
        key, value = key.strip(), value.strip()
        if value:
            mapping[key] = _scalar(value)
        elif index < len(lines) and lines[index][0] > indent:
            mapping[key], index = _parse_block(lines, index, lines[index][0])
        else:
            # A key with nothing under it means an empty list (`tags:` with no items).
            mapping[key] = []
    return mapping, index


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the strict frontmatter subset used in this repo.

    Supports ``key: value`` scalars, ``key:`` followed by ``  - item`` lists, and
    nested mappings one or more levels deep. Returns the mapping plus the body that
    follows the closing delimiter.
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    lines: list[tuple[int, str]] = []
    for raw_line in match.group(1).expandtabs(2).splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append((len(raw_line) - len(raw_line.lstrip(" ")), stripped))

    if not lines:
        return {}, text[match.end():]
    data, _ = _parse_block(lines, 0, lines[0][0])
    return (data if isinstance(data, dict) else {}), text[match.end():]


def topic_title(directory: str, readme_text: str | None = None) -> str:
    """Topic display name, taken from the topic README frontmatter when present."""
    if readme_text:
        meta, _ = parse_frontmatter(readme_text)
        if meta.get("title"):
            return str(meta["title"])
    return directory.replace("-", " ").title()


def load_topics(root: Path = REPO_ROOT) -> list[Topic]:
    topics: list[Topic] = []
    for directory, meta_entry in topic_meta().items():
        entry = root / directory
        if not entry.is_dir():
            continue
        readme = entry / "README.md"
        topic = Topic(
            directory=directory,
            order=int(meta_entry.get("order", 0)),
            title=topic_title(
                directory, readme.read_text(encoding="utf-8") if readme.exists() else None
            ),
        )
        for md in sorted(entry.glob("*.md")):
            if md.name == "README.md":
                continue
            file_match = QUESTION_FILE_RE.match(md.name)
            if not file_match:
                continue
            meta, body = parse_frontmatter(md.read_text(encoding="utf-8"))
            topic.questions.append(
                Question(
                    path=md,
                    slug=file_match.group(1),
                    title=str(meta.get("title", "")),
                    id=int(meta["id"]) if str(meta.get("id", "")).isdigit() else -1,
                    category=str(meta.get("category", "")),
                    difficulty=str(meta.get("difficulty", "")),
                    tags=list(meta.get("tags", [])),
                    body=body,
                    quiz=meta["quiz"] if isinstance(meta.get("quiz"), dict) else None,
                )
            )
        topic.questions.sort(key=lambda q: q.id)
        topics.append(topic)
    topics.sort(key=lambda t: t.order)
    return topics


def all_questions(topics: list[Topic]) -> list[Question]:
    return [q for topic in topics for q in topic.questions]


def normalize_markdown(text: str) -> str:
    """Collapse formatting-only differences so generated and formatted files compare equal.

    Prettier pads Markdown table cells to align columns; the generator emits compact
    tables. Both are the same document, so comparisons ignore runs of whitespace and
    the dash padding in table separator rows.
    """
    lines = []
    for line in text.strip().splitlines():
        line = re.sub(r"\s+", " ", line.strip())
        if set(line) <= set("|- :") and "|" in line:
            line = re.sub(r"-{2,}", "---", line)
        lines.append(line)
    return "\n".join(lines)


def replace_block(text: str, marker: str, payload: str) -> str:
    """Replace content between ``<!-- MARKER:START -->``/``<!-- MARKER:END -->``."""
    start, end = f"<!-- {marker}:START -->", f"<!-- {marker}:END -->"
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end), re.DOTALL
    )
    # Blank lines around the markers keep the output stable under Prettier.
    block = f"{start}\n\n{payload.strip()}\n\n{end}"
    if not pattern.search(text):
        raise SystemExit(f"marker {marker} not found - cannot generate index")
    return pattern.sub(lambda _: block, text, count=1)
