# Contributing

Thanks for helping improve this collection. Corrections, deeper answers, and new questions are all welcome.

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
python3 scripts/generate_indexes.py     # rewrite all indexes from the question files
python3 scripts/validate_content.py     # frontmatter, naming, links, index freshness
```

Both are stdlib-only Python 3.11+ - nothing to install.

Then run the two Markdown checks CI runs. Neither needs a `package.json`; `npx` fetches them on demand:

```bash
npx prettier@3 --write "**/*.md"        # formatting (config: .prettierrc.json)
npx markdownlint-cli2 "**/*.md"         # linting   (config: .markdownlint-cli2.jsonc)
```

Run the generator _before_ Prettier. The generator emits compact tables and Prettier pads them into aligned columns; comparisons are whitespace-normalised, so running them in that order settles and neither tool undoes the other.

A few linter conventions worth knowing, all deliberate and encoded in `.markdownlint-cli2.jsonc`:

- **Bold lead-ins** (`**Trade-offs**`) are used to label a paragraph inside a section without adding it to the heading outline - `MD036` is disabled for this.
- **Every code fence needs a language.** Use `text` for ASCII diagrams and plain output.
- **Line length is unlimited** (`MD013` off) - write one paragraph per line and let the editor wrap.

### 5. Open the pull request

Fill in the [pull request template](./.github/pull_request_template.md). CI runs the same two scripts plus Prettier on every pull request.

## Adding a new topic

1. Create `topic-slug/` (no number).
2. Add an entry to `scripts/topic_meta.json` with an `order` (where it appears in the indexes), a `description`, and a few `study_notes` (the "What interviewers probe here" bullets). A directory that is not registered here fails validation.
3. Create `topic-slug/README.md` with frontmatter containing the topic `title` - the generator reads the display name from there, then rewrites the rest of the file.
4. Add your question files, then run the generator and validator.

## Style

- British or American spelling is fine; be consistent within a file.
- Prefer tables for comparisons, bullets for enumerations, prose for reasoning.
- Keep code examples minimal and correct. If it would not run, do not ship it.
- Pin versions in examples where the version matters.
