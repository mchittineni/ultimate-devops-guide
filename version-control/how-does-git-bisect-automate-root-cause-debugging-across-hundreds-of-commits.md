---
title: "How does Git Bisect automate root-cause debugging across hundreds of commits?"
id: 580
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - git
  - bisect
  - debugging
  - automation
quiz:
  stem: "What requirement must an automated test script satisfy to be used with `git bisect run <script>`?"
  options:
    - "It must be written exclusively in Python"
    - "It must exit with status code 0 if the commit is good/clean, and non-zero (1-127) if the commit is bad/broken"
    - "It must output a JSON report to `/tmp/results.json`"
    - "It must execute in under 5 milliseconds"
  answer: 2
  explanation: "`git bisect run` relies on standard Unix process exit codes: exit code 0 marks the commit as 'good', exit codes between 1 and 127 mark it as 'bad'."
---

# How does Git Bisect automate root-cause debugging across hundreds of commits?

**Short answer:** `git bisect` uses a binary search algorithm through the commit history to pinpoint the exact commit that introduced a bug in $O(\log N)$ steps, capable of running fully automated with a test script.

## Detail

If an application passed tests 500 commits ago but is currently failing in production, manually testing commits takes hours. Binary search finds the culprit in $\approx 9$ checks ($\log_2 500 \approx 8.9$).

### Interactive Bisect

```bash
git bisect start
git bisect bad                 # Current commit is broken
git bisect good v1.4.0         # v1.4.0 was known to be working
# Git checks out the midpoint commit (~250)
# You test the application...
git bisect bad                 # If bug is present
# Git checks out midpoint of remaining good/bad...
```

### Fully Automated Bisect with a Script

You can automate the entire investigation using any command or script that returns exit code 0 (good) or 1-127 (bad). Exit code **125** is special: it tells bisect the commit cannot be tested (it does not build, say) and should be skipped; codes above 127 abort the bisect:

```bash
git bisect run pytest tests/test_payment.py
```

Git checks out commits automatically, runs the test suite, marks good/bad based on exit code, and reports:
`1e2f3a4b is the first bad commit`.

### Practical details and limits

- **Untestable commits** (broken builds in the middle of history) are skipped with `git bisect skip` or exit 125; too many of them and bisect can only narrow the culprit to a range.
- **Merges**: `git bisect start --first-parent` follows only the mainline, so you find the merge that introduced the bug rather than a commit deep inside a feature branch.
- **Flaky tests poison bisect**: one wrong good/bad answer sends the search down the wrong half. Make the script deterministic, or run the check several times per commit.
- **Custom terms**: `--term-old=fast --term-new=slow` for hunting performance regressions rather than bugs.
- Always finish with `git bisect reset` to return to where you started; `git bisect log` records the session so it can be replayed.

## Example

```bash
# A bisect script: build, then test; 125 = "skip this commit"
cat > /tmp/bisect.sh <<'EOF'
#!/usr/bin/env bash
make build >/dev/null 2>&1 || exit 125      # cannot build: skip, do not blame it
pytest -q tests/test_payment.py              # 0 = good, 1 = bad
EOF
chmod +x /tmp/bisect.sh

git bisect start --first-parent HEAD v1.4.0  # bad, then good
git bisect run /tmp/bisect.sh
# 1e2f3a4b is the first bad commit
git bisect log > bisect.log                  # keep the evidence
git bisect reset                             # back to where you started
```

## Interview tips

- Explain it as binary search over history: about $\log_2 N$ tests, so ~10 for 1,000 commits.
- Know the `bisect run` exit-code contract, including 125 for "skip".
- Mention `--first-parent` for merge-heavy histories and the danger of flaky tests.
- Keep the script outside the working tree (as above), because bisect checks out old commits that may not contain it.
- Likely follow-up: "what makes history bisectable?" - small commits that each build and pass tests.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between trunk-based development and GitFlow in modern continuous delivery?]] (`#537`): [What is the difference between trunk-based development and GitFlow in modern continuous delivery?](../cicd/what-is-the-difference-between-trunk-based-development-and-gitflow-in-modern-continuous-delivery.md)
- [[What is Semantic Release and how does it automate versioning and changelogs from commits?]] (`#540`): [What is Semantic Release and how does it automate versioning and changelogs from commits?](../cicd/what-is-semantic-release-and-how-does-it-automate-versioning-and-changelogs-from-commits.md)
- [[What is Packer and how does it automate immutable golden machine image generation across clouds?]] (`#632`): [What is Packer and how does it automate immutable golden machine image generation across clouds?](../devops-tools-and-automation/what-is-packer-and-how-does-it-automate-immutable-golden-machine-image-generation-across-clouds.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
