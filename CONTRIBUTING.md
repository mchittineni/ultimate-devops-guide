# Contributing

Thanks for helping improve this collection. Corrections, deeper answers, and new questions are all welcome.

Participation is covered by the [Code of Conduct](./CODE_OF_CONDUCT.md) - which also carries the three rules specific to this project: **share questions, never people** (no naming or describing interviewers), **respect confidentiality** (nothing under NDA, no take-home assignments or their solutions), and **no plagiarism** (write answers in your own words, link sources rather than copying them). Security problems - a committed credential, a workflow vulnerability, or malicious example code - go through the [Security Policy](./SECURITY.md) privately, never a public issue.

If you would rather suggest than write, the [issue templates](./.github/ISSUE_TEMPLATE/) cover a new question, a correction to an existing answer, an interview experience, a new topic, and broken links or tooling.

## What makes a good contribution

The bar here is **an answer that would land well in a real interview** - not a definition copied from documentation. Concretely:

- Explain the mechanism, not just the name. "Kubernetes reconciles desired state" beats "Kubernetes is an orchestrator."
- Include a trade-off or a limitation. Answers with no downsides read as rehearsed.
- Show a real example - a command, a manifest, a snippet you have actually run.
- Say what the interviewer is likely to ask next.

## Adding or editing a question

### 1. File location and name

```text
topic-slug/question-title-slug.md
```

- **No numeric prefixes** on directories or filenames - they are pure slugs.
- The slug **must** match the title: lowercase, non-alphanumerics collapsed to `-`, `&` becomes `and`. `validate_content.py` enforces this, and will tell you the expected slug if you get it wrong.
- Ordering lives in metadata, not filenames: `id` in each question's frontmatter, and `order` in `scripts/topic_meta.json` for topics.

### 2. Frontmatter

Every question file starts with:

```yaml
---
title: "What is Kubernetes?"
id: 11
category: "Kubernetes"
difficulty: "Beginner"
tags:
  - devops
  - kubernetes
  - interview-questions
---
```

- `id` must be unique across the whole repository, and must match the number in the `#` heading.
- `category` must exactly match the topic README's `title`.
- `difficulty` is one of `Beginner`, `Intermediate`, `Advanced`.
- `tags` must include `devops` and `interview-questions`, plus the topic slug.

### 3. Body structure

````markdown
# What is Kubernetes?

**Short answer:** two or three sentences.

## Detail

The substance - mechanisms, trade-offs, vocabulary.

## Example

```yaml
# real, runnable, minimal
```

## Interview tips

- The follow-up questions and common traps.

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
````

The `# <title>` heading must match the frontmatter exactly.

**Do not indent prose by four spaces.** Markdown renders it as a code block; the validator rejects it.

### 4. Regenerate indexes and validate

Topic READMEs and the root README's table of contents are **generated**. Never edit them by hand - your change will be overwritten and CI will fail.

```bash
python3 scripts/generate_indexes.py        # rewrite all indexes from the question files
python3 scripts/inject_wikilinks.py        # inject cross-topic [[wikilinks]]
python3 scripts/build_knowledge_graph.py   # regenerate 3D knowledge graph (docs/index.html)
python3 scripts/build_quiz_data.py         # regenerate the quiz data feed (docs/data/)
python3 scripts/validate_content.py        # frontmatter, naming, links, index freshness
```

All are stdlib-only Python 3.11+ - nothing to install.

Then run the two Markdown checks CI runs. Neither needs a `package.json`; `npx` fetches them on demand:

```bash
npx prettier@3.9.10 --write "**/*.md"          # formatting (config: .prettierrc.json)
npx markdownlint-cli2@0.24.0 "**/*.md"         # linting   (config: .markdownlint-cli2.jsonc)
```

Run the generator _before_ Prettier. The generator emits compact tables and Prettier pads them into aligned columns; comparisons are whitespace-normalised, so running them in that order settles and neither tool undoes the other.

A few linter conventions worth knowing, all deliberate and encoded in `.markdownlint-cli2.jsonc`:

- **Bold lead-ins** (`**Trade-offs**`) are used to label a paragraph inside a section without adding it to the heading outline - `MD036` is disabled for this.
- **Every code fence needs a language.** Use `text` for ASCII diagrams and plain output.
- **Line length is unlimited** (`MD013` off) - write one paragraph per line and let the editor wrap.

### 5. Open the pull request

Fill in the [pull request template](./.github/pull_request_template.md). On every pull request CI runs:

- `validate_content.py`, plus `--check` mode of the index, knowledge-graph, and quiz-feed generators, so committed output can never drift from the question files.
- Prettier and markdownlint, at the versions pinned in [`validate-and-format.yml`](./.github/workflows/validate-and-format.yml).
- `ruff check`, `ruff format --check`, and the unit tests under `tests/`.
- `actionlint` and the `zizmor` security audit over the workflows.

If you change anything under `scripts/`, run the same Python checks locally. Ruff is dev-only; the scripts themselves stay stdlib-only:

```bash
python3 -m unittest discover -s tests       # unit tests and generator freshness checks
pipx run ruff==0.17.3 check scripts tests   # lint (config: ruff.toml)
pipx run ruff==0.17.3 format scripts tests  # format
```

## Adding a new topic

1. Create `topic-slug/` (no number).
2. Add an entry to `scripts/topic_meta.json` with an `order` (where it appears in the indexes), a `description`, and a few `study_notes` (the "What interviewers probe here" bullets). A directory that is not registered here fails validation.
3. Create `topic-slug/README.md` with frontmatter containing the topic `title` - the generator reads the display name from there, then rewrites the rest of the file.
4. Add your question files, then run the generator and validator.

## Translations

English is canonical. Everything else is derived from it in one of two ways:

| What                                         | Where                             | How it is made                                                                                                               |
| -------------------------------------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Landing pages** - one per language         | `i18n/README.<code>.md` on `main` | Translated by hand, reviewed like any other change.                                                                          |
| **Lessons** - every topic index and question | `i18n/<code>/` on `translations`  | Machine-translated by the [Translate Lessons](./.github/workflows/translate-lessons.yml) workflow after each push to `main`. |

- **To fix a lesson translation, fix the English original.** The workflow retranslates any page whose English source changed; the `translations` branch is rebuilt and force-pushed on every run, so edits made there are lost.
- **To fix a landing page,** edit `i18n/README.<code>.md` directly. Leave the `LANGS` and `BADGES` marker blocks alone - `generate_indexes.py` writes them, and CI fails if they drift.
- **To add a language:** add an entry to `scripts/i18n.json` (code, native `name`, the `english_name` the translator is prompted with, the localised `label` for the language bar, and the `mt_notice` shown on machine-translated pages, with `{source}` where the link to the English original goes). Copy an existing `i18n/README.<code>.md` for the new code and translate it, then run `generate_indexes.py`. The language bar on every page picks it up, and the next workflow run translates the lessons.

The workflow needs an `ANTHROPIC_API_KEY` repository secret and skips without one; the `TRANSLATE_MODEL` repository variable overrides the model. To preview what a run would translate, without calling the API:

```bash
python3 scripts/translate_lessons.py --lang es --dry-run
```

## Style

- British or American spelling is fine; be consistent within a file.
- Prefer tables for comparisons, bullets for enumerations, prose for reasoning.
- Keep code examples minimal and correct. If it would not run, do not ship it.
- Pin versions in examples where the version matters.
