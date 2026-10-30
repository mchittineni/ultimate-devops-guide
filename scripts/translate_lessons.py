#!/usr/bin/env python3
"""Machine-translate lesson pages into one language, for the translations branch.

English is canonical. This script never touches ``main``'s content: it writes
``i18n/<code>/<topic>/<file>.md`` - a mirror of every topic index and question
file - which the Translate Lessons workflow publishes on the ``translations``
branch. The hand-translated landing page ``i18n/README.<code>.md`` is copied in as
``i18n/<code>/README.md`` so the translated tree has a home page.

Translation is incremental. ``i18n/<code>/.manifest.json`` records the hash of
each English source a translation was made from; only new or changed sources are
sent to the model, and translations whose source was deleted are removed.

Code blocks and ``[[wikilinks]]`` are swapped for placeholders before the text
goes to the model and restored afterwards, so commands, config, and Obsidian
links are never translated. A translation that loses or duplicates a placeholder
is rejected and retried on the next run.

Usage:
    python3 scripts/translate_lessons.py --lang es              # translate what changed
    python3 scripts/translate_lessons.py --lang es --dry-run    # list work, call nothing
    python3 scripts/translate_lessons.py --lang es --limit 50   # cap files this run

Environment:
    ANTHROPIC_API_KEY       required unless --dry-run
    TRANSLATE_MODEL         default claude-opus-5-5
    TRANSLATE_EFFORT        default low
    TRANSLATE_CONCURRENCY   parallel requests, default 4

Requires the ``anthropic`` package (CI installs it); the rest of scripts/ stays
stdlib-only. Exit codes: 0 = done (per-file failures are reported and retried next
run), 1 = bad arguments, 2 = the API rejected the credentials or model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from lib_content import FRONTMATTER_RE, I18N_DIR, REPO_ROOT, i18n_config, landing_page, load_topics

# Bump when the prompt or post-processing changes enough to warrant retranslating everything.
PROMPT_VERSION = "1"

DEFAULT_MODEL = "claude-opus-5-5"
# Models that take the server-side refusal fallback and the effort parameter.
FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5", "claude-fable-5-1"}
FALLBACK_BETA = "server-side-fallback-2026-07-01"

LINK_RE = re.compile(r"(\]\()([^)\s]+)(\))")
WIKILINK_RE = re.compile(r"\[\[[^\]\n]+\]\]")
PLACEHOLDER_RE = re.compile(r"⟦[CW]\d+⟧")
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")

SYSTEM_PROMPT = """You translate Markdown pages from English into {language} for an open-source \
DevOps, SRE, cloud, and platform-engineering interview-preparation guide. Reply with the \
translated Markdown only: no preamble, no notes, and no code fence around the whole reply.

Rules:
1. Keep the Markdown structure identical: the same heading levels, lists, tables (same rows \
and columns), blockquotes, emphasis, and blank lines.
2. Tokens such as ⟦C3⟧ and ⟦W7⟧ are placeholders for code blocks and wiki links. Copy every \
placeholder exactly once, unchanged, where it belongs in the sentence. A placeholder that \
stands alone on a line stays alone on its line.
3. Never translate inline code (text in backticks), URLs, link targets, file paths, commands, \
flags, configuration keys, or HTML. Do translate the visible text of links.
4. Keep product, tool, and service names in English (Kubernetes, Terraform, AWS Lambda, \
Prometheus, GitHub Actions). Keep technical terms in English where {language}-speaking \
engineers normally use the English word (for example pod, pipeline, rollback, canary); you \
may add a short translation in parentheses the first time such a term appears.
5. Keep emoji, including the difficulty markers 🟢 🟡 🔴.
6. Write in a clear, professional register for engineers preparing for interviews."""


def source_files() -> list[str]:
    """Repo-relative paths of every page that gets translated, in index order."""
    files = []
    for topic in load_topics():
        files.append(f"{topic.directory}/README.md")
        files += [f"{topic.directory}/{q.filename}" for q in topic.questions]
    return files


def digest(text: str) -> str:
    return hashlib.sha256(f"{PROMPT_VERSION}\n{text}".encode("utf-8")).hexdigest()


def rewrite_links(text: str, src_rel: str, dest_rel: str, translated: set[str], out_rel: str) -> str:
    """Point relative links at the right file once the page moves under ``i18n/<code>/``.

    A link to another translated page follows it into the translated tree; any other
    relative link (the English README, CONTRIBUTING.md, images) points back at the
    original file, which sits beside the translations on the branch.
    """
    src_dir, dest_dir = posixpath.dirname(src_rel), posixpath.dirname(dest_rel)

    def fix(match: re.Match) -> str:
        target = match.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:|^#|^/", target, re.I):
            return match.group(0)
        path, _, anchor = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(src_dir, path))
        if resolved.startswith(".."):
            return match.group(0)
        full = posixpath.join(out_rel, resolved) if resolved in translated else resolved
        new = posixpath.relpath(full, dest_dir or ".")
        if not new.startswith("."):
            new = f"./{new}"
        return f"{match.group(1)}{new}{'#' + anchor if anchor else ''}{match.group(3)}"

    return LINK_RE.sub(fix, text)


def mask(body: str) -> tuple[str, dict[str, str]]:
    """Swap fenced code blocks and wikilinks for placeholders the model must copy through."""
    saved: dict[str, str] = {}
    out: list[str] = []
    block: list[str] = []
    fence: str | None = None
    indent = ""
    for line in body.split("\n"):
        if fence is None:
            opening = FENCE_RE.match(line)
            if opening:
                indent, fence, block = opening.group(1), opening.group(2), [line]
                continue
            out.append(line)
            continue
        block.append(line)
        if line.strip().startswith(fence[0] * len(fence)) and line.strip().strip(fence[0]) == "":
            key = f"⟦C{len(saved)}⟧"
            saved[key] = "\n".join(block)
            out.append(f"{indent}{key}")
            fence = None
    if fence is not None:  # unterminated fence: leave it as text
        out += block
    masked = "\n".join(out)

    def wiki(match: re.Match) -> str:
        key = f"⟦W{len(saved)}⟧"
        saved[key] = match.group(0)
        return key

    return WIKILINK_RE.sub(wiki, masked), saved


def unmask(text: str, saved: dict[str, str]) -> str:
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        # A code-block placeholder on its own line is replaced by the whole original block,
        # which carries its own indentation.
        if stripped.startswith("⟦C") and stripped in saved:
            lines.append(saved[stripped])
        else:
            lines.append(line)
    text = "\n".join(lines)
    return PLACEHOLDER_RE.sub(lambda m: saved.get(m.group(0), m.group(0)), text)


def check_placeholders(masked: str, translated: str) -> str | None:
    want = sorted(PLACEHOLDER_RE.findall(masked))
    got = sorted(PLACEHOLDER_RE.findall(translated))
    if want != got:
        missing = sorted(set(want) - set(got))
        extra = sorted(set(got) - set(want)) or [k for k in set(got) if got.count(k) > 1]
        return f"placeholders changed (missing {missing}, unexpected {extra})"
    return None


def strip_wrapper(text: str) -> str:
    """Remove a ```markdown fence the model occasionally wraps the whole reply in."""
    text = text.strip()
    match = re.fullmatch(r"```(?:markdown|md)?\n(.*)\n```", text, re.S)
    return match.group(1).strip() if match else text


class Translator:
    def __init__(self, language: str, model: str, effort: str):
        import anthropic  # CI-only dependency; imported lazily so --dry-run needs nothing

        self.anthropic = anthropic
        self.client = anthropic.Anthropic(max_retries=6)
        self.model = model
        self.effort = effort
        self.system = SYSTEM_PROMPT.replace("{language}", language)

    def __call__(self, markdown: str) -> str:
        kwargs: dict = {
            "model": self.model,
            "max_tokens": 64000,
            "system": self.system,
            "messages": [{"role": "user", "content": markdown}],
        }
        if self.model in FALLBACK_MODELS:
            kwargs["output_config"] = {"effort": self.effort}
            kwargs["betas"] = [FALLBACK_BETA]
            kwargs["extra_body"] = {"fallbacks": "default"}
        with self.client.beta.messages.stream(**kwargs) as stream:
            message = stream.get_final_message()
        if message.stop_reason != "end_turn":
            raise RuntimeError(f"stopped with {message.stop_reason}")
        return "".join(block.text for block in message.content if block.type == "text")


def translate_file(
    rel: str, lang: dict, out_rel: str, translated_set: set[str], translate
) -> str:
    source = (REPO_ROOT / rel).read_text(encoding="utf-8")
    dest_rel = f"{out_rel}/{rel}"
    match = FRONTMATTER_RE.match(source)
    frontmatter, body = (match.group(0), source[match.end():]) if match else ("", source)

    masked, saved = mask(body)
    # After masking, so links inside code blocks are left exactly as written.
    # A lesson's "All topics" link to the root README lands on the translated home page.
    masked = rewrite_links(masked, rel, dest_rel, translated_set | {"README.md"}, out_rel)
    result = strip_wrapper(translate(masked))
    problem = check_placeholders(masked, result)
    if problem:
        raise RuntimeError(problem)

    english = posixpath.relpath(rel, posixpath.dirname(dest_rel))
    notice = "> 🌐 " + lang["mt_notice"].replace("{source}", english)
    page = f"{frontmatter}\n{notice}\n\n{unmask(result, saved)}\n"
    return page if frontmatter else page.lstrip("\n")


def write_home(lang: dict, out_rel: str, translated_set: set[str]) -> None:
    """Copy the committed landing page in as the translated tree's README."""
    src = landing_page(lang["code"])
    src_rel = src.relative_to(REPO_ROOT).as_posix()
    dest_rel = f"{out_rel}/README.md"
    # The landing page's own ../README.md links mean "the English original", so the root
    # README is deliberately not in the set of pages that follow into the translated tree.
    text = rewrite_links(src.read_text(encoding="utf-8"), src_rel, dest_rel, translated_set, out_rel)
    (REPO_ROOT / dest_rel).write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lang", required=True, help="language code from scripts/i18n.json")
    parser.add_argument("--limit", type=int, default=0, help="translate at most N files this run")
    parser.add_argument("--dry-run", action="store_true", help="list pending work without calling the API")
    args = parser.parse_args()

    languages = {lang["code"]: lang for lang in i18n_config()["languages"]}
    if args.lang not in languages:
        print(f"unknown language {args.lang!r}; choose from {', '.join(languages)}", file=sys.stderr)
        return 1
    lang = languages[args.lang]
    out_dir = I18N_DIR / lang["code"]
    out_rel = out_dir.relative_to(REPO_ROOT).as_posix()
    manifest_path = out_dir / ".manifest.json"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    done: dict[str, str] = manifest.get("files", {})
    sources = source_files()
    translated_set = set(sources)

    for rel in sorted(set(done) - translated_set):
        (out_dir / rel).unlink(missing_ok=True)
        del done[rel]
        print(f"removed  {rel} (English source deleted)")

    hashes = {rel: digest((REPO_ROOT / rel).read_text(encoding="utf-8")) for rel in sources}
    pending = [rel for rel in sources if done.get(rel) != hashes[rel] or not (out_dir / rel).exists()]
    if args.limit:
        pending = pending[: args.limit]

    print(f"{lang['name']} ({lang['code']}): {len(sources)} pages, {len(pending)} to translate")
    if args.dry_run:
        chars = sum(len(mask((REPO_ROOT / rel).read_text(encoding="utf-8"))[0]) for rel in pending)
        for rel in pending:
            print(f"  pending  {rel}")
        print(f"~{chars:,} characters of prose to translate (code blocks excluded)")
        return 0

    model = os.environ.get("TRANSLATE_MODEL") or DEFAULT_MODEL
    translate = Translator(lang["english_name"], model, os.environ.get("TRANSLATE_EFFORT") or "low")
    workers = int(os.environ.get("TRANSLATE_CONCURRENCY") or 4)
    lock = threading.Lock()
    failures: list[str] = []
    fatal: list[str] = []

    def save() -> None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"prompt_version": PROMPT_VERSION, "model": model, "files": dict(sorted(done.items()))}
        manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def work(rel: str) -> None:
        if fatal:
            return
        try:
            page = translate_file(rel, lang, out_rel, translated_set, translate)
        except (
            translate.anthropic.AuthenticationError,
            translate.anthropic.PermissionDeniedError,
            translate.anthropic.NotFoundError,
        ) as exc:
            fatal.append(f"{type(exc).__name__}: {exc}")
            return
        except Exception as exc:  # one bad page must not sink the rest of the run
            with lock:
                failures.append(f"{rel}: {exc}")
            print(f"failed   {rel}: {exc}", flush=True)
            return
        dest = out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        with lock:
            done[rel] = hashes[rel]
            if len(done) % 25 == 0:
                save()  # a timed-out job still keeps what it finished
        print(f"done     {rel}", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for future in as_completed([pool.submit(work, rel) for rel in pending]):
            future.result()

    save()
    out_dir.mkdir(parents=True, exist_ok=True)
    write_home(lang, out_rel, translated_set)

    if fatal:
        print(f"\nStopped: the API rejected the request - {fatal[0]}", file=sys.stderr)
        return 2
    print(f"\nTranslated {len(pending) - len(failures)} page(s); {len(failures)} failed.")
    for failure in failures:
        print(f"  - {failure}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
