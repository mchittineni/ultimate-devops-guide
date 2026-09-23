---
title: "How does Git internally store data using Blobs, Trees, Commits, and Annotated Tags?"
id: 578
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - git
  - internals
  - blobs
  - trees
  - objects
quiz:
  stem: "In Git's internal object database, which object type is responsible for storing a file's name and POSIX execution permissions?"
  options:
    - "The Blob object"
    - "The Tree object"
    - "The Commit object"
    - "The Reflog object"
  answer: 2
  explanation: "Blobs store only raw file content. The Tree object acts as a directory, recording the mapping between filenames, file permissions (modes), and the corresponding Blob or Sub-tree SHAs."
---

# How does Git internally store data using Blobs, Trees, Commits, and Annotated Tags?

**Short answer:** Git is a content-addressable key-value object database stored under `.git/objects/`, where each object's ID is the hash of its type, size, and content (SHA-1 by default, SHA-256 in repositories created with `--object-format=sha256`). There are four object types: Blobs (raw file contents), Trees (directories and filenames), Commits (tree pointer, parents, author, committer, message), and annotated Tags (a named, optionally signed pointer to another object).

## Detail

Understanding Git's four object primitives demystifies virtually all Git behavior:

```text
Commit Object (points to author, parent commit SHA, and root Tree)
   └── Tree Object (directory: maps filename 'src' to Tree, 'README' to Blob)
          └── Blob Object (raw content of README.md - no filename or permissions)
```

1. **Blob**: Stores only raw file bytes (compressed with zlib). It does **not** store the filename, directory path, or permissions. If two files in different directories have identical content, Git stores only one blob!
2. **Tree**: Represents a directory. Stores a list of mode (permissions), type (blob or tree), object SHA, and filename.
3. **Commit**: A small text file containing:
   - Pointer to top-level root Tree SHA.
   - Parent commit SHA(s).
   - Author and committer identities with timestamps, and an optional signature (GPG, SSH, or X.509).
   - Commit message.
4. **Annotated Tag**: A tag object pointing at another object (usually a commit) with its own tagger, date, message, and optional signature. A **lightweight** tag, by contrast, is not an object at all - just a ref file containing a commit ID.

Branches and lightweight tags are **refs** - small files (or entries in `packed-refs`) under `.git/refs/` that contain an object ID. Moving a branch is rewriting one line; the objects never change, which is why history rewrites create new commits rather than editing old ones.

### Storage in practice

New objects are written as zlib-compressed **loose objects** (`.git/objects/ab/cdef...`). `git gc` (and automatic maintenance) packs them into **packfiles**, where similar objects are stored as deltas against each other - which is why a repository full of slightly changed files stays small. Note the hash choice: SHA-1 in Git uses collision detection (hardened against the SHAttered attack), and SHA-256 repositories are supported but still have limited interoperability with forges, so most repositories remain SHA-1 for now.

## Example

```bash
git init demo && cd demo
echo "hello" > README.md
git add README.md && git commit -qm "first"
git tag -a v1.0 -m "release 1.0"

git cat-file -t HEAD              # commit
git cat-file -p HEAD              # tree <sha> / author ... / committer ... / message
git cat-file -p 'HEAD^{tree}'     # 100644 blob <sha>    README.md  (mode + name live here)
git cat-file -p HEAD:README.md    # hello                (the blob: content only)
git cat-file -t v1.0              # tag  (an annotated tag is its own object)
git hash-object README.md         # same ID as the blob above: content-addressed
git count-objects -v              # loose vs packed objects
```

## Interview tips

- Name the four object types and what each stores - especially that filenames and modes live in trees, not blobs.
- Explain content addressing: identical content gives an identical ID, which gives deduplication and integrity checking for free.
- Distinguish refs (mutable pointers) from objects (immutable); it explains branches, rebases, and the reflog.
- Contrast annotated and lightweight tags, and mention signing.
- Know the hash story: SHA-1 with collision detection by default, SHA-256 available.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between trunk-based development and GitFlow in modern continuous delivery?]] (`#537`): [What is the difference between trunk-based development and GitFlow in modern continuous delivery?](../cicd/what-is-the-difference-between-trunk-based-development-and-gitflow-in-modern-continuous-delivery.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[What is GitLab CI?]] (`#19`): [What is GitLab CI?](../cicd/what-is-gitlab-ci.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
