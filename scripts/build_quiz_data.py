#!/usr/bin/env python3
"""Generate the static quiz data feed consumed by the quiz web app.

The markdown vault stays the single source of truth. This script flattens it into
versioned JSON under ``docs/data/`` so it publishes with the GitHub Pages artifact
and any external front end can fetch it without parsing markdown:

    docs/data/manifest.json        topic registry, counts, and file index
    docs/data/topics/<slug>.json   every question in one topic, quiz block included
    docs/data/quiz.json            only the questions carrying a `quiz:` block

Usage:
    python3 scripts/build_quiz_data.py                    # write the feed
    python3 scripts/build_quiz_data.py --check            # fail if the feed is stale
    python3 scripts/build_quiz_data.py --output-dir DIR   # write somewhere else
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib_content import DIFFICULTIES, REPO_ROOT, Question, Topic, all_questions, load_topics, topic_meta

SCHEMA_VERSION = 1
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "data"
DEFAULT_REPO_URL = "https://github.com/mchittineni/ultimate-devops-guide"
DEFAULT_BRANCH = "main"

SHORT_ANSWER_RE = re.compile(r"^\*\*Short answer:\*\*\s*(.+?)\s*$", re.M)
SECTION_RE = re.compile(r"^## (.+?)\s*$", re.M)
# Generated "Related Concepts" rows carry the target question id: (`#11`)
RELATED_RE = re.compile(r"\(`#(\d+)`\)")


def short_answer(question: Question) -> str:
    """The one-line answer a candidate can say out loud, or '' if the body lacks one."""
    match = SHORT_ANSWER_RE.search(question.body)
    return match.group(1).strip() if match else ""


def sections(question: Question) -> list[str]:
    return [name for name in SECTION_RE.findall(question.body)]


def difficulty_counts(questions: list[Question]) -> dict[str, int]:
    return {level: sum(1 for q in questions if q.difficulty == level) for level in DIFFICULTIES}


def quiz_payload(question: Question) -> dict | None:
    """Normalize the frontmatter quiz block: 1-based `answer` becomes a 0-based index."""
    if not question.quiz:
        return None
    quiz = question.quiz
    options = [str(o) for o in quiz.get("options", [])]
    answer = str(quiz.get("answer", "")).strip()
    return {
        "stem": str(quiz.get("stem") or question.title),
        "options": options,
        "answerIndex": int(answer) - 1 if answer.isdigit() else -1,
        "explanation": str(quiz.get("explanation", "")),
    }


def question_payload(question: Question, by_id: dict[int, Question], repo_url: str, branch: str) -> dict:
    rel_path = question.path.relative_to(REPO_ROOT).as_posix()
    related = []
    for raw_id in RELATED_RE.findall(question.body):
        target = by_id.get(int(raw_id))
        if target is None or target.id == question.id:
            continue
        related.append(
            {
                "id": target.id,
                "slug": target.slug,
                "title": target.title,
                "topic": target.topic_dir,
            }
        )
    return {
        "id": question.id,
        "slug": question.slug,
        "title": question.title,
        "topic": question.topic_dir,
        "category": question.category,
        "difficulty": question.difficulty,
        "tags": question.tags,
        "path": rel_path,
        "url": f"{repo_url}/blob/{branch}/{rel_path}",
        "shortAnswer": short_answer(question),
        "sections": sections(question),
        "related": related,
        "quiz": quiz_payload(question),
    }


def build_feed(topics: list[Topic], repo_url: str, branch: str) -> dict[str, dict]:
    """Return a mapping of output-relative file path -> JSON-serializable payload."""
    meta = topic_meta()
    questions = all_questions(topics)
    by_id = {q.id: q for q in questions}

    files: dict[str, dict] = {}
    topic_entries: list[dict] = []
    quiz_items: list[dict] = []

    for topic in topics:
        payloads = [question_payload(q, by_id, repo_url, branch) for q in topic.questions]
        entry_meta = meta.get(topic.directory, {})
        rel_file = f"topics/{topic.directory}.json"
        files[rel_file] = {
            "schemaVersion": SCHEMA_VERSION,
            "slug": topic.directory,
            "title": topic.title,
            "group": entry_meta.get("group", ""),
            "description": entry_meta.get("description", ""),
            "studyNotes": entry_meta.get("study_notes", []),
            "questions": payloads,
        }
        topic_entries.append(
            {
                "slug": topic.directory,
                "title": topic.title,
                "group": entry_meta.get("group", ""),
                "description": entry_meta.get("description", ""),
                "order": topic.order,
                "file": rel_file,
                "counts": {
                    "questions": len(payloads),
                    "quiz": sum(1 for p in payloads if p["quiz"]),
                    "byDifficulty": difficulty_counts(topic.questions),
                },
            }
        )
        for payload in payloads:
            if payload["quiz"]:
                quiz_items.append(
                    {
                        key: payload[key]
                        for key in (
                            "id",
                            "slug",
                            "title",
                            "topic",
                            "category",
                            "difficulty",
                            "tags",
                            "path",
                            "url",
                            "shortAnswer",
                            "quiz",
                        )
                    }
                )

    files["manifest.json"] = {
        "schemaVersion": SCHEMA_VERSION,
        "source": {"repo": repo_url, "branch": branch},
        "counts": {
            "topics": len(topics),
            "questions": len(questions),
            "quiz": len(quiz_items),
            "byDifficulty": difficulty_counts(questions),
        },
        "topics": topic_entries,
    }
    files["quiz.json"] = {
        "schemaVersion": SCHEMA_VERSION,
        "source": {"repo": repo_url, "branch": branch},
        "count": len(quiz_items),
        "questions": quiz_items,
    }
    return files


def serialize(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if any generated file is missing or stale",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="print errors only")
    args = parser.parse_args()

    topics = load_topics()
    files = build_feed(topics, args.repo_url.rstrip("/"), args.branch)

    stale: list[str] = []
    for rel, payload in sorted(files.items()):
        target = args.output_dir / rel
        text = serialize(payload)
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != text:
                stale.append(rel)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    # A topic that was renamed or removed leaves an orphan file behind.
    topics_dir = args.output_dir / "topics"
    expected = {rel for rel in files}
    if topics_dir.is_dir():
        for existing in sorted(topics_dir.glob("*.json")):
            rel = f"topics/{existing.name}"
            if rel in expected:
                continue
            if args.check:
                stale.append(f"{rel} (orphan - topic no longer registered)")
            else:
                existing.unlink()

    manifest = files["manifest.json"]["counts"]
    if args.check:
        if stale:
            print(
                f"{len(stale)} quiz data file(s) stale - run `python3 scripts/build_quiz_data.py`:",
                file=sys.stderr,
            )
            for rel in stale:
                print(f"  - {rel}", file=sys.stderr)
            return 1
        if not args.quiet:
            print(f"Quiz data feed up to date ({manifest['questions']} questions).")
        return 0

    if not args.quiet:
        rel_dir = args.output_dir.relative_to(REPO_ROOT) if args.output_dir.is_relative_to(REPO_ROOT) else args.output_dir
        print(f"Wrote {len(files)} file(s) to {rel_dir}")
        print(f"Topics:     {manifest['topics']}")
        print(f"Questions:  {manifest['questions']}")
        print(f"Quiz-ready: {manifest['quiz']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
