# Security Policy

This repository is a **content vault**: Markdown answers plus a small amount of stdlib-only Python that generates and validates the indexes. It ships no application, no container image, and no published package. That shapes what a vulnerability means here - the realistic risks are in the automation, in the examples people copy, and in credentials that should never have been committed.

## Supported versions

| Version              | Supported                               |
| -------------------- | --------------------------------------- |
| `main`               | ✅ Fixes land here                      |
| Tags, forks, mirrors | ❌ Not maintained - re-pull from `main` |

There is no release train. `main` is always the supported state of the content and the tooling.

## Reporting a vulnerability

**Do not open a public issue for a security problem.** Use GitHub's private reporting instead:

1. Go to the repository's **Security** tab.
2. Choose **Report a vulnerability** (private vulnerability reporting).
3. Include the details below.

If private reporting is unavailable to you, contact the maintainer directly on GitHub - [@mchittineni](https://github.com/mchittineni) - and ask for a private channel before sending details.

Please include:

- What the issue is, and which file, workflow, or script it affects.
- How to reproduce it, ideally with the exact command or a link to a workflow run.
- What an attacker gains - the impact, not just the mechanism.
- Any suggested fix, if you have one.

### What to expect

| Stage                    | Target                                                                          |
| ------------------------ | ------------------------------------------------------------------------------- |
| Acknowledgement          | Within 5 working days                                                           |
| Initial assessment       | Within 10 working days - accepted, needs more information, or out of scope      |
| Fix for accepted reports | As soon as practical; credential exposure and workflow issues are treated first |
| Credit                   | Offered in the fix commit or advisory unless you prefer to stay anonymous       |

This is a volunteer-maintained project, so these are honest targets rather than contractual commitments. Please give a reasonable window before disclosing publicly, and do not exploit an issue beyond what is needed to demonstrate it.

## In scope

- **GitHub Actions workflows** in [.github/workflows/](.github/workflows/) - script injection through untrusted input (`pull_request_target` handling, expression interpolation of PR titles, branch names, or file contents), excessive `GITHUB_TOKEN` permissions, unpinned or compromised third-party actions, or any path by which a fork's pull request could obtain write access or read secrets.
- **The Python tooling** in [scripts/](scripts/) - path traversal or writes outside the repository, unsafe handling of file contents, or anything that turns running `python3 scripts/generate_indexes.py` on a clone into code execution.
- **Committed secrets** - any real credential, token, key, connection string, certificate, or internal hostname that has been committed to this repository, whether in an answer's example or in the tooling. Report these privately and urgently.
- **Malicious content** - an "example" command, manifest, or script whose real effect is destructive, exfiltrating, or obfuscated (typosquatted package names, piped installers pointing at attacker infrastructure, base64 payloads).
- **Supply-chain surface of the local toolchain** - the `npx prettier@3` / `npx markdownlint-cli2` invocations contributors are asked to run, and the actions referenced by the workflows.

## Out of scope

- Vulnerabilities in the third-party tools that the answers _describe_ (Kubernetes, Terraform, Jenkins, cloud services). Report those to their maintainers.
- **Deliberately insecure snippets used to illustrate a problem** - for example a hardcoded credential shown as the wrong way to do it, an over-permissive IAM policy in a "what not to do" example, or a `NetworkPolicy` that is intentionally too open. If one is not clearly labelled as an anti-pattern, that is a content bug worth an ordinary issue.
- Examples that are simplified for teaching and would need hardening for production - see the note below.
- Typos, broken links, stale versions, and factual errors. Open a normal issue for these.
- Findings from an automated scanner with no demonstrated impact on this repository.

## Rules for contributors

These prevent most of what would otherwise become a security report:

1. **Never commit a real secret.** Use obvious placeholders - `AKIAIOSFODNN7EXAMPLE`, `sha256:9f2c8b1d...`, `example.com`, `<your-account-id>`, `changeme`. Never paste a token "with a few characters changed".
2. **If you commit a secret, treat it as compromised.** Rotate or revoke it first, then report it privately. Deleting the line does not remove it from Git history, and force-pushing over a public repository does not guarantee the object is gone from forks, caches, or clones.
3. **Never include real internal identifiers** - production hostnames, account IDs, cluster endpoints, ARNs, internal IP ranges, or customer names. Redact them.
4. **Keep examples safe to paste.** Assume a reader will run your command verbatim on a real machine. Prefer read-only diagnostic commands; where a command is destructive (`docker system prune -a --volumes`, `kubectl delete`, `terraform destroy`, `rm -rf`), say so in the surrounding text.
5. **Do not add workflow changes that expand permissions** without explaining why in the pull request. `pull_request_target`, `permissions: write-all`, and unpinned actions get extra scrutiny.

## Note on the content itself

Every example here is written to be correct and runnable, but it is written to **teach a concept in an interview context** - not as a hardened production template. Answers often omit TLS setup, network restrictions, quotas, tagging, and audit configuration to keep the point visible. Review anything you take from this repository against your own organisation's standards before it reaches a real environment, and treat security-related answers - IAM, secrets, admission control, network policy - as a starting point for design rather than a finished configuration.

---

[⬅ Back to the guide](./README.md) · [Contributing](./CONTRIBUTING.md) · [Code of Conduct](./CODE_OF_CONDUCT.md)
