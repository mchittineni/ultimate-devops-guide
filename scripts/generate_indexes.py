#!/usr/bin/env python3
"""Regenerate every index in the repo from the question files themselves.

Rewrites each topic ``README.md`` in full, and replaces the ``TOC`` and ``STATS``
marker blocks in the root ``README.md``. Run after adding or renaming any
question; CI fails if the committed indexes differ from what this produces.

Usage:
    python3 scripts/generate_indexes.py            # write indexes
    python3 scripts/generate_indexes.py --check    # report drift, write nothing
"""

from __future__ import annotations

import argparse

from lib_content import (
    REPO_ROOT,
    Topic,
    all_questions,
    load_topics,
    normalize_markdown,
    replace_block,
    topic_meta,
)

DIFFICULTY_BADGE = {
    "Beginner": "🟢 Beginner",
    "Intermediate": "🟡 Intermediate",
    "Advanced": "🔴 Advanced",
}

# Themed sections for the root README, in display order. Each topic declares its
# group in topic_meta.json; a topic whose group is unlisted falls into "Other".
GROUP_ORDER = [
    ("Foundations", "🧱"),
    ("Containers and Kubernetes", "📦"),
    ("Delivery and Automation", "🔁"),
    ("Cloud Providers", "☁️"),
    ("Architecture and Scale", "🏗️"),
    ("Reliability and Operations", "📈"),
    ("Security", "🔐"),
    ("Platform and Leadership", "🧭"),
]


def grouped_topics(topics: list[Topic]) -> list[tuple[str, str, list[Topic]]]:
    """Topics bucketed into the themed sections used by the root README."""
    meta = topic_meta()
    buckets: dict[str, list[Topic]] = {name: [] for name, _ in GROUP_ORDER}
    for topic in topics:
        group = str(meta.get(topic.directory, {}).get("group", "Other"))
        buckets.setdefault(group, []).append(topic)
    emoji = dict(GROUP_ORDER)
    ordered = [name for name, _ in GROUP_ORDER] + [
        name for name in buckets if name not in emoji
    ]
    return [
        (name, emoji.get(name, "📚"), buckets[name]) for name in ordered if buckets.get(name)
    ]


def difficulty_counts(questions) -> dict[str, int]:
    return {
        level: sum(1 for q in questions if q.difficulty == level)
        for level in ("Beginner", "Intermediate", "Advanced")
    }


def render_topic_readme(topic: Topic, _current: str | None = None) -> str:
    meta = topic_meta().get(topic.directory, {})
    slug_tag = topic.directory
    lines = [
        "---",
        f'title: "{topic.title}"',
        f'category: "{topic.title}"',
        "tags:",
        "  - devops",
        f"  - {slug_tag}",
        "  - index",
        "---",
        "",
        f"# {topic.title}",
        "",
        meta.get("description", f"Interview questions and answers for **{topic.title}**."),
        "",
        f"**{len(topic.questions)} questions** · "
        + " · ".join(
            f"{DIFFICULTY_BADGE.get(level, level)}: "
            f"{sum(1 for q in topic.questions if q.difficulty == level)}"
            for level in ("Beginner", "Intermediate", "Advanced")
        ),
        "",
        "## Questions",
        "",
        "| # | Question | Difficulty |",
        "| --- | --- | --- |",
    ]
    for q in topic.questions:
        lines.append(
            f"| {q.id} | [{q.title}](./{q.filename}) | "
            f"{DIFFICULTY_BADGE.get(q.difficulty, q.difficulty)} |"
        )
    if not topic.questions:
        lines.append("| — | _No questions yet — contributions welcome._ | — |")

    if meta.get("study_notes"):
        lines += ["", "## What interviewers probe here", ""]
        lines += [f"- {note}" for note in meta["study_notes"]]

    lines += ["", "---", "", "[⬅ Back to all topics](../README.md)", ""]
    return "\n".join(lines)


def render_root_toc(topics: list[Topic]) -> str:
    """Every question, as one collapsible block per topic under a themed heading.

    Collapsed by default: 230+ rows in a single table is a wall of text, whereas
    one ``<details>`` per topic lets a reader open only what they are studying.
    """
    lines: list[str] = []
    for group, emoji, group_topics in grouped_topics(topics):
        group_questions = all_questions(group_topics)
        lines += [f"### {emoji} {group}", "", f"_{len(group_questions)} questions_", ""]
        for topic in group_topics:
            per = difficulty_counts(topic.questions)
            lines += [
                "<details>",
                f"<summary><b>{topic.title}</b> · {len(topic.questions)} questions · "
                f"🟢 {per['Beginner']} 🟡 {per['Intermediate']} 🔴 {per['Advanced']}</summary>",
                "",
                f"[Open the {topic.title} index →](./{topic.directory}/README.md)",
                "",
                "| No. | Question | Difficulty |",
                "| --- | --- | --- |",
            ]
            for q in topic.questions:
                lines.append(
                    f"| {q.id} | [{q.title}](./{topic.directory}/{q.filename}) | "
                    f"{DIFFICULTY_BADGE.get(q.difficulty, q.difficulty)} |"
                )
            if not topic.questions:
                lines.append("| — | _No questions yet — contributions welcome._ | — |")
            lines += ["", "</details>", ""]
    return "\n".join(lines).strip()


def render_stats(topics: list[Topic]) -> str:
    questions = all_questions(topics)
    counts = difficulty_counts(questions)
    lines = [
        f"**{len(questions)} questions** across **{len(topics)} topics** — "
        f"🟢 {counts['Beginner']} Beginner · 🟡 {counts['Intermediate']} Intermediate · "
        f"🔴 {counts['Advanced']} Advanced",
        "",
    ]
    meta = topic_meta()
    for group, emoji, group_topics in grouped_topics(topics):
        lines += [
            f"### {emoji} {group}",
            "",
            "| Topic | Questions | 🟢 | 🟡 | 🔴 | What it covers |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for topic in group_topics:
            per = difficulty_counts(topic.questions)
            summary = str(meta.get(topic.directory, {}).get("description", "")).split(":", 1)
            blurb = (summary[1] if len(summary) > 1 else summary[0]).strip()
            blurb = blurb[:97].rsplit(" ", 1)[0] + "…" if len(blurb) > 100 else blurb
            lines.append(
                f"| **[{topic.title}](./{topic.directory}/README.md)** | "
                f"{len(topic.questions)} | {per['Beginner']} | {per['Intermediate']} | "
                f"{per['Advanced']} | {blurb} |"
            )
        lines.append("")
    return "\n".join(lines).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    args = parser.parse_args()

    topics = load_topics()
    drifted: list[str] = []

    for topic in topics:
        target = topic.path / "README.md"
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        rendered = render_topic_readme(topic, current)
        # Only rewrite on a real content change, so Prettier's column padding survives.
        if normalize_markdown(rendered) != normalize_markdown(current):
            drifted.append(str(target.relative_to(REPO_ROOT)))
            if not args.check:
                target.write_text(rendered, encoding="utf-8")

    root_path = REPO_ROOT / "README.md"
    root = root_path.read_text(encoding="utf-8")
    updated = replace_block(root, "TOC", render_root_toc(topics))
    updated = replace_block(updated, "STATS", render_stats(topics))
    if normalize_markdown(updated) != normalize_markdown(root):
        drifted.append("README.md")
        if not args.check:
            root_path.write_text(updated, encoding="utf-8")

    if args.check:
        if drifted:
            print("Stale indexes (run `python3 scripts/generate_indexes.py`):")
            for item in drifted:
                print(f"  - {item}")
            return 1
        print("Indexes are up to date.")
        return 0

    print(f"Updated {len(drifted)} index file(s)." if drifted else "Indexes already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
