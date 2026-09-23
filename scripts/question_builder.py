#!/usr/bin/env python3
"""Shared helper to write out question markdown files with valid frontmatter,
body, code examples, interview tips, and quiz blocks.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def slugify(title: str) -> str:
    slug = title.lower()
    slug = slug.replace("&", " and ")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def write_question(
    *,
    id: int,
    title: str,
    topic_dir: str,
    category: str,
    difficulty: str,
    tags: list[str],
    short_answer: str,
    detail: str,
    listen_for: list[str],
    related: list[tuple[str, str]],  # (concept_name, relative_path)
    quiz: dict,  # {"stem": ..., "options": [...], "answer": 1-based int, "explanation": ...}
) -> Path:
    # Ensure mandatory tags
    all_tags = list(dict.fromkeys(["devops", "interview-questions"] + tags))

    slug = slugify(title)
    target_dir = REPO_ROOT / topic_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / f"{slug}.md"

    # Format YAML frontmatter
    tags_formatted = "\n".join(f"  - {t}" for t in all_tags)
    quiz_options = "\n".join(f'    - "{opt}"' for opt in quiz["options"])
    quiz_stem = f'  stem: "{quiz["stem"]}"\n' if quiz.get("stem") else ""
    quiz_explanation = quiz["explanation"].replace('"', '\\"')

    frontmatter = f"""---
title: "{title}"
id: {id}
category: "{category}"
difficulty: "{difficulty}"
tags:
{tags_formatted}
quiz:
{quiz_stem}  options:
{quiz_options}
  answer: {quiz["answer"]}
  explanation: "{quiz_explanation}"
---
"""

    # Format related section
    if related:
        related_lines = "\n".join(f"- [{name}]({path})" for name, path in related)
    else:
        related_lines = f"- [DevOps Roadmap](../README.md)"

    # Format interview tips
    tips_lines = "\n".join(f"- {tip}" for tip in listen_for)

    content = f"""{frontmatter}
# {title}

**Short answer:** {short_answer.strip()}

## Detail

{detail.strip()}

## What the interviewer is listening for

{tips_lines}

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

{related_lines}

<!-- END GENERATED RELATED TOPICS -->
"""


    target_file.write_text(content, encoding="utf-8")
    return target_file
