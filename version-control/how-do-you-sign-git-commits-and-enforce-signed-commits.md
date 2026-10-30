---
title: "How do you sign Git commits and enforce signed commits?"
id: 760
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - version-control
  - interview-questions
  - git
  - security
  - supply-chain
quiz:
  stem: "What does a valid signature on a Git commit actually prove?"
  options:
    - "That the code in the commit has been reviewed and is safe"
    - "That the commit was created by the holder of the signing key and has not been altered since it was signed"
    - "That the commit passed CI"
    - "That the author email in the commit is the real author"
  answer: 2
  explanation: "A commit signature binds the commit object (tree, parents, metadata, message) to a key. It proves possession of that key and integrity of the commit, not code quality or review. The author field itself is unauthenticated text, which is exactly why signing matters: anyone can set user.email to someone else's address."
---

# How do you sign Git commits and enforce signed commits?

**Short answer:** Git can attach a cryptographic signature to commits and tags with a **GPG key**, an **SSH key** (Git 2.34+), or an **X.509 certificate** (including keyless Sigstore certificates via `gitsign`). You set `gpg.format`, `user.signingkey`, and `commit.gpgsign=true`, and the forge shows the commit as "Verified" when the key is registered to the committer's account. Enforcement happens on the server: a branch protection rule or ruleset that **requires signed commits**, or a GitLab push rule that rejects unsigned ones. The reason it matters: Git's author and committer fields are just text - anyone can commit as `ceo@example.com` - and a signature is the only thing that ties a commit to a key the person controls.

## Detail

### What signing does and does not prove

The signature covers the commit object - tree, parents, author, committer, message - so any change to the commit invalidates it. It proves that someone holding the key created this exact commit. It does **not** prove the code was reviewed, that the person is still trustworthy, or that the key was not stolen. Treat it as one control in a supply-chain chain (with review, branch protection, and build provenance), not as a guarantee.

### The three signing formats

| Format    | Key material                                                         | Strengths                                                    | Trade-offs                                                                                         |
| --------- | -------------------------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| **GPG**   | OpenPGP key                                                          | Long-standing, supported everywhere, subkeys and expiry      | Key management is painful; developers lose keys, agents misbehave                                  |
| **SSH**   | The SSH key you already use (ideally a hardware-backed `ed25519-sk`) | Simplest adoption; reuse existing keys; works with forges    | Local verification needs an `allowedSignersFile`; no built-in expiry/revocation                    |
| **X.509** | Corporate PKI certificate, or Sigstore via `gitsign`                 | Ties signatures to corporate identity or OIDC login; keyless | Forge "Verified" support depends on the CA - GitHub does not mark `gitsign` signatures as verified |

SSH signing is what most teams adopt today because it removes the GPG learning curve. `gitsign` signs with a short-lived certificate issued after an OIDC login and records it in the Rekor transparency log - attractive for supply-chain auditability, but you verify it with `gitsign verify` or policy tooling rather than relying on the forge badge.

### Enforcing it

- **GitHub**: branch protection "Require signed commits", or a repository/organisation **ruleset** with the same rule, so unsigned commits cannot reach protected branches. Enable **vigilant mode** on your account so unsigned commits attributed to you are flagged as "Unverified".
- **GitLab**: the "Reject unsigned commits" push rule (premium tiers), plus protected branches.
- **Self-hosted Git**: a `pre-receive` hook running `git verify-commit` against an allowed-signers list.
- **In CI or policy**: verify signatures on release tags before building, so a release cannot be cut from an unsigned tag.

### The practical problems

- **Web-UI merges and squashes** are created by the forge, which signs them with its own key - so "every commit on `main` is signed" often means "signed by GitHub", and the individual author's signature lives on the PR branch commits.
- **Rebasing rewrites commits**, so they must be re-signed; with `commit.gpgsign=true` Git does this automatically, but a teammate rebasing your branch replaces your signature with theirs.
- **Bots and automation** must sign too: use a GitHub App or the API (commits created through it are signed by the platform), or give the bot its own SSH signing key.
- **Key loss and rotation**: an SSH key removed from the account can turn old commits "Unverified" on some forges; plan rotation, prefer hardware-backed keys, and keep signing keys separate from authentication keys if your policy requires it.

## Example

```bash
# SSH signing (Git 2.34+) - the lowest-friction setup
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
git config --global tag.gpgsign true
# then add the same public key on the forge as a *signing* key

# Local verification needs a list of trusted signers
echo "alice@example.com $(cat ~/.ssh/id_ed25519.pub)" >> ~/.config/git/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.config/git/allowed_signers

git commit -m "fix: tighten session timeout"
git log --show-signature -1        # Good "git" signature for alice@example.com
git verify-commit HEAD && git tag -s v1.4.0 -m "1.4.0" && git verify-tag v1.4.0
```

```bash
# Keyless Sigstore signing with gitsign (X.509, short-lived certs, transparency log)
git config --local gpg.x509.program gitsign
git config --local gpg.format x509
git config --local commit.gpgsign true
git commit -m "feat: add audit log"   # browser OIDC login, cert issued, entry in Rekor
gitsign verify --certificate-identity=alice@example.com \
  --certificate-oidc-issuer=https://accounts.google.com HEAD
```

```bash
# Enforce on GitHub: require signed commits on main via branch protection
gh api -X POST repos/acme/app/branches/main/protection/required_signatures
```

## Interview tips

- Start with why: author fields are unauthenticated, so without signatures anyone can impersonate anyone in history.
- Know all three formats and recommend SSH signing for adoption, with `gitsign` as the keyless supply-chain option and its forge-verification caveat.
- Say precisely what a signature proves (key possession and integrity) and what it does not (review, intent, safety).
- Enforcement is server-side - branch protection or rulesets requiring signed commits, push rules, or `pre-receive` hooks - just as with every other client-side control.
- Mention the squash-merge and rebase caveats; they are what trip teams up after they turn the rule on.
- Likely follow-up: "how does this relate to SLSA?" - commit signing strengthens the source side; build provenance covers how the artefact was built. See [SLSA and build integrity](../cicd/what-are-slsa-supply-chain-levels-for-software-artifacts-frameworks-and-how-do-they-verify-build-integrity.md) and [how Git stores commits and tags](./how-does-git-internally-store-data-using-blobs-trees-commits-and-annotated-tags.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you secure CI/CD runners against supply-chain attacks and untrusted pull requests?]] (`#538`): [How do you secure CI/CD runners against supply-chain attacks and untrusted pull requests?](../cicd/how-do-you-secure-ci-cd-runners-against-supply-chain-attacks-and-untrusted-pull-requests.md)
- [[What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?]] (`#539`): [What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?](../cicd/what-are-slsa-supply-chain-levels-for-software-artifacts-frameworks-and-how-do-they-verify-build-integrity.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
