---
title: "How do you secure CI/CD runners against supply-chain attacks and untrusted pull requests?"
id: 538
category: "CI/CD"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - cicd
  - security
  - supply-chain
  - runners
quiz:
  stem: "Why is pinning third-party CI/CD actions by full 40-character commit SHA more secure than pinning by version tag (like `@v4`)?"
  options:
    - "Commit SHAs download 50% faster than semantic tags"
    - "Git tags are mutable and can be quietly rewritten by an attacker to point to malicious code; commit SHAs are immutable cryptographic hashes"
    - "GitHub Actions rejects any workflow referencing semantic version tags"
    - "Commit SHAs automatically execute automated vulnerability scans"
  answer: 2
  explanation: "A compromised action maintainer account or compromised repository can retag `v4` to point to a malicious commit that steals secrets. Cryptographic SHAs are immutable."
---

# How do you secure CI/CD runners against supply-chain attacks and untrusted pull requests?

**Short answer:** Secure runners use sandboxed ephemeral execution, restrict secret exposure on `pull_request_target` triggers, pin actions by full commit SHA instead of mutable tags, and run with unprivileged user permissions and restricted egress networks.

## Detail

A CI runner holds exactly what an attacker wants - secrets, a write token to the repository, cloud credentials, and the ability to publish artefacts - and it executes code from pull requests and third-party actions. Every hardening measure below either reduces what a job can reach or reduces the untrusted code that runs next to it.

### Key Hardening Measures

1. **Dangers of `pull_request_target`**: In GitHub Actions, `pull_request_target` runs in the context of the base branch and has access to repository secrets. If a workflow checks out the untrusted fork's code (`actions/checkout@v7 with: ref: ${{ github.event.pull_request.head.sha }}`) and executes build scripts, the PR author can dump repository secrets.
2. **Pin Actions to Commit SHA**:

   ```yaml
   # Vulnerable to tag hijacking:
   uses: actions/checkout@v7
   # Secure against malicious tag mutability:
   uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
   ```

   GitHub now lets administrators **enforce** this: the allowed-actions policy can require full-SHA pinning (unpinned `uses:` fails the run) and block specific actions or versions. Pinning the SHA does not pin what the action itself downloads at runtime, so prefer actions without unpinned transitive fetches, and let Dependabot or Renovate bump the SHAs.

3. **Network Egress Filtering**: Restrict build runner outbound traffic. If an untrusted build script attempts to send environment variables to an external command-and-control server, egress firewall rules or eBPF agents block the connection.
4. **Read-Only Permissions by Default**:

   ```yaml
   permissions:
     contents: read
   ```

   Set the organisation default for `GITHUB_TOKEN` to read-only and grant `id-token: write`, `packages: write` and similar per job, only where needed.

5. **Ephemeral, isolated runners**: one job per runner, destroyed afterwards (GitHub-hosted runners, Actions Runner Controller with ephemeral pods, `--ephemeral` self-hosted runners). A persistent self-hosted runner lets one malicious job plant a backdoor that the next, trusted job inherits. Never attach persistent self-hosted runners to public repositories.
6. **Gate untrusted contributors**: require approval before workflows run for first-time or outside contributors, and keep `pull_request_target` / `workflow_run` workflows free of any step that executes PR-controlled code (build scripts, `npm install` lifecycle hooks, Makefiles).
7. **Avoid script injection**: never interpolate attacker-controlled fields (`${{ github.event.pull_request.title }}`, branch names, issue bodies) directly into `run:`; pass them through `env:` and quote them.

The trade-off is friction: SHA pinning needs a bot to stay current, egress allowlists break when a build legitimately needs a new host, and approval gates slow outside contributions. Those costs are small compared with a leaked deploy credential.

## Example

```yaml
# Safe split: untrusted build with no secrets, privileged step that never runs PR code
name: pr
on:
  pull_request: # fork PRs get a read-only token and no secrets

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: step-security/harden-runner@e14015d583714f6e62063499dc959a02595150a1 # v2.21.1
        with:
          egress-policy: block # only the endpoints below are reachable
          allowed-endpoints: >
            github.com:443
            registry.npmjs.org:443
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false # do not leave the token in .git/config
      - name: Use PR metadata safely
        env:
          TITLE: ${{ github.event.pull_request.title }} # via env, never inline in run:
        run: echo "Building: $TITLE"
      - run: npm ci --ignore-scripts && npm test
```

## Interview tips

- Explain `pull_request` versus `pull_request_target` precisely: the latter runs with the base repository's secrets and a write token, so checking out and executing the PR head in it hands both to the PR author.
- Say why SHAs beat tags (tags are mutable; a compromised maintainer can repoint `v4`), and mention that organisations can now enforce SHA pinning by policy - then name the limitation that pinning does not cover what the action downloads at runtime.
- Least-privilege `GITHUB_TOKEN`, ephemeral runners, and egress filtering are the three controls that shrink blast radius when prevention fails.
- Mention script injection via `${{ }}` in `run:` - it is the most common workflow vulnerability after `pull_request_target` misuse.
- Likely follow-up: "how do you give a deploy job cloud access without secrets?" - OIDC federation with a trust policy scoped to the repository, branch, and environment.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What is HashiCorp Vault and how does dynamic secret generation eliminate static credentials?]] (`#631`): [What is HashiCorp Vault and how does dynamic secret generation eliminate static credentials?](../devops-tools-and-automation/what-is-hashicorp-vault-and-how-does-dynamic-secret-generation-eliminate-static-credentials.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
