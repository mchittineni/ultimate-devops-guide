#!/usr/bin/env python3
"""Validate the question vault: frontmatter, naming, IDs, links, and indexes.

Usage:
    python3 scripts/validate_content.py          # validate everything
    python3 scripts/validate_content.py --quiet  # errors only

Exit codes: 0 = clean, 1 = validation errors found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from lib_content import (
    DIFFICULTIES,
    QUESTION_FILE_RE,
    REPO_ROOT,
    all_questions,
    load_topics,
    normalize_markdown,
    topic_meta,
)

REQUIRED_TAGS = {"devops", "interview-questions"}
LINK_RE = re.compile(r"\[[^\]]*\]\((\.[^)\s]+)\)")
HEADING_RE = re.compile(r"^# (.+)$", re.M)


def strip_code_blocks(text: str) -> str:
    """Blank out fenced code blocks so their contents are not linted as prose."""
    out, fence = [], None
    for line in text.splitlines():
        marker = line.lstrip()
        if fence is None and marker.startswith("```"):
            fence = "`" * (len(marker) - len(marker.lstrip("`")))
            out.append("")
            continue
        if fence is not None:
            if marker.startswith(fence):
                fence = None
            out.append("")
            continue
        out.append(line)
    return "\n".join(out)


def slugify(title: str) -> str:
    slug = title.lower()
    slug = slug.replace("&", " and ")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def check_questions(topics, errors: list[str]) -> None:
    seen_ids: dict[int, Path] = {}
    for topic in topics:
        for q in topic.questions:
            rel = q.path.relative_to(REPO_ROOT)

            if not q.title:
                errors.append(f"{rel}: missing `title` in frontmatter")
            if q.id < 0:
                errors.append(f"{rel}: missing or non-numeric `id` in frontmatter")
            elif q.id in seen_ids:
                errors.append(
                    f"{rel}: duplicate id {q.id} (also {seen_ids[q.id].relative_to(REPO_ROOT)})"
                )
            else:
                seen_ids[q.id] = q.path

            if q.category != topic.title:
                errors.append(
                    f"{rel}: category '{q.category}' does not match topic '{topic.title}'"
                )
            if q.difficulty not in DIFFICULTIES:
                errors.append(
                    f"{rel}: difficulty '{q.difficulty}' not one of {', '.join(DIFFICULTIES)}"
                )
            missing_tags = REQUIRED_TAGS - set(q.tags)
            if missing_tags:
                errors.append(f"{rel}: missing required tag(s): {', '.join(sorted(missing_tags))}")

            expected_slug = slugify(q.title)
            if q.title and q.slug != expected_slug:
                errors.append(
                    f"{rel}: filename slug '{q.slug}' should be '{expected_slug}' for this title"
                )

            heading = HEADING_RE.search(q.body)
            if not heading:
                errors.append(f"{rel}: body must start with a `# <title>` heading")
            elif heading.group(1).strip() != q.title:
                errors.append(f"{rel}: heading text does not match frontmatter title")

            # Indented prose outside a fence silently renders as a code block.
            in_fence = False
            for line in q.body.splitlines():
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                if line.startswith("    ") and not line.strip().startswith(("-", "*", "|")):
                    errors.append(
                        f"{rel}: 4-space indented prose renders as a code block - de-indent it"
                    )
                    break


def check_links(errors: list[str]) -> None:
    for md in sorted(REPO_ROOT.rglob("*.md")):
        if ".git" in md.parts or "node_modules" in md.parts:
            continue
        text = strip_code_blocks(md.read_text(encoding="utf-8"))
        for target in LINK_RE.findall(text):
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            if not (md.parent / path_part).resolve().exists():
                errors.append(f"{md.relative_to(REPO_ROOT)}: broken link -> {target}")


def check_indexes(topics, errors: list[str]) -> None:
    """Fail if generated indexes are stale relative to the question files."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_indexes import render_root_toc, render_stats, render_topic_readme

    for topic in topics:
        readme = topic.path / "README.md"
        if not readme.exists():
            errors.append(f"{topic.directory}/README.md: missing topic index")
            continue
        current = readme.read_text(encoding="utf-8")
        if normalize_markdown(render_topic_readme(topic, current)) != normalize_markdown(current):
            errors.append(
                f"{topic.directory}/README.md: stale - run `python3 scripts/generate_indexes.py`"
            )

    root = normalize_markdown((REPO_ROOT / "README.md").read_text(encoding="utf-8"))
    for marker, payload in (("TOC", render_root_toc(topics)), ("STATS", render_stats(topics))):
        if normalize_markdown(payload) not in root:
            errors.append(
                f"README.md: {marker} block is stale - run `python3 scripts/generate_indexes.py`"
            )


def check_orphan_files(errors: list[str]) -> None:
    """Catch topic directories that exist on disk but are not registered, and bad filenames."""
    registered = set(topic_meta())
    skip = {"scripts", ".git", ".github", "node_modules"}
    for entry in sorted(p for p in REPO_ROOT.iterdir() if p.is_dir()):
        if entry.name in skip or entry.name.startswith("."):
            continue
        if entry.name not in registered:
            errors.append(
                f"{entry.name}/: directory is not registered in scripts/topic_meta.json"
            )
            continue
        for md in sorted(entry.glob("*.md")):
            if md.name != "README.md" and not QUESTION_FILE_RE.match(md.name):
                errors.append(
                    f"{md.relative_to(REPO_ROOT)}: filename must match question-slug.md"
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", "-q", action="store_true", help="print errors only")
    args = parser.parse_args()

    topics = load_topics()
    questions = all_questions(topics)
    errors: list[str] = []

    check_orphan_files(errors)
    check_questions(topics, errors)
    check_links(errors)
    check_indexes(topics, errors)

    if not args.quiet:
        print(f"Topics:    {len(topics)}")
        print(f"Questions: {len(questions)}")
        ids = sorted(q.id for q in questions if q.id > 0)
        if ids:
            gaps = sorted(set(range(ids[0], ids[-1] + 1)) - set(ids))
            print(f"ID range:  {ids[0]}-{ids[-1]}" + (f" (gaps: {gaps})" if gaps else " (no gaps)"))

    if errors:
        print(f"\n{len(errors)} validation error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    if not args.quiet:
        print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
