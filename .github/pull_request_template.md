## Description

<!-- What does this PR add or change? -->

## Type of Change

- [ ] 🆕 New interview question(s) and answer(s)
- [ ] 📝 Improving an existing answer
- [ ] 📁 New topic directory
- [ ] 🔧 Fixing links, formatting, or tooling

## Topic

<!-- The topic directory, e.g. `kubernetes`, `cloud-platforms` -->

- **Directory**:

## Checklist

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full format.

- [ ] **File name** is `topic-slug/question-slug.md` — no numeric prefix, and the slug matches the title.
- [ ] **Frontmatter** includes `title`, a unique `id`, `category` matching the topic title, a `difficulty` of Beginner/Intermediate/Advanced, and the required tags.
- [ ] **Heading** is `# <title>` and matches the frontmatter exactly.
- [ ] **Answer structure** follows Short answer → Detail → Example → Interview tips.
- [ ] **New topic only**: registered in `scripts/topic_meta.json` with an `order`, `description`, and `study_notes`.
- [ ] Ran `python3 scripts/generate_indexes.py` (indexes are generated — do not hand-edit topic READMEs or the root TOC).
- [ ] Ran `python3 scripts/validate_content.py` and it passed.
- [ ] Content is accurate, and any code examples actually work.
