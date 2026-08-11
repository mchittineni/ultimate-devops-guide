---
title: "How do you provide self-service environments to developers?"
id: 227
category: "Platform Engineering"
difficulty: "Advanced"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# How do you provide self-service environments to developers?

**Short answer:** Make environments ephemeral, created from a pull request and destroyed on merge, using a namespace or lightweight cluster with the service under test deployed fresh and its dependencies either shared-but-isolated or virtualised. The three problems to solve are data seeding, dependency simulation, and cost - and the discipline that makes it work is a hard time-to-live on every environment.

## Detail

**Patterns, from cheapest to most faithful:**

| Pattern                             | Fidelity | Cost   | Notes                                                          |
| ----------------------------------- | -------- | ------ | -------------------------------------------------------------- |
| Local (Compose/kind/Tilt)           | low–med  | free   | fastest loop; drifts from production                           |
| Ephemeral namespace per PR          | medium   | low    | the common default; shares cluster services                    |
| Request-level isolation (sandboxes) | high     | low    | route test traffic through shared services with tenant headers |
| Ephemeral cluster per PR            | high     | high   | needed when cluster-scoped resources are in play               |
| Shared long-lived staging           | medium   | medium | contended, drifts, still needed for some tests                 |

**Data is the real work.** Options: a seeded minimal fixture set (fast, deterministic, and usually correct), an anonymised production subset (realistic, requires a maintained anonymisation pipeline and a privacy review), or copy-on-write database clones/snapshots (fast, realistic, provider-dependent). Copying production data unmasked into a developer environment is a data-protection incident waiting to be discovered by an auditor.

**Dependencies: three honest choices.** Deploy the full stack per environment (faithful, expensive, slow - impractical past a handful of services); point at shared dependency instances with per-environment isolation via tenant IDs or namespacing (the common compromise); or use contract-tested stubs and service virtualisation for third parties (fast and deterministic, with the risk that stubs drift from reality - contract tests are what keep them honest).

**Cost control is non-negotiable.** Mandatory TTL with automatic deletion, scale-to-zero or nightly shutdown outside working hours, per-team budgets with visible spend, and Spot/preemptible capacity for non-critical environments. Without a TTL, ephemeral environments become long-lived ones and the bill grows quietly - the most common failure of these systems.

**Feedback speed determines adoption.** If an environment takes 25 minutes to appear, developers stop using it. Target a few minutes: pre-warmed capacity, cached images, pre-provisioned database templates rather than fresh instances, and deploying only the changed service against shared dependencies. Post the environment URL back to the pull request automatically.

**Where this replaces staging, and where it does not.** Ephemeral environments handle feature verification, review, and integration tests well. Load testing, long-running migration rehearsals, and full disaster-recovery drills still need a persistent, production-like environment. And nothing here removes the need for progressive delivery in production - canaries with real traffic catch what no pre-production environment can.

## Example

```yaml
# PR-scoped environment with a hard TTL and automatic teardown
name: preview-environment
on:
  pull_request:
    types: [opened, synchronize, closed]
jobs:
  deploy:
    if: github.event.action != 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create namespace with TTL label
        run: |
          NS="pr-${{ github.event.number }}"
          kubectl create namespace "$NS" --dry-run=client -o yaml | kubectl apply -f -
          kubectl label namespace "$NS" --overwrite \
            acme.com/ttl=8h acme.com/owner="${{ github.actor }}" acme.com/pr="${{ github.event.number }}"
      - name: Clone the database template (seconds, not minutes)
        run: ./scripts/clone-db-template.sh "pr-${{ github.event.number }}"
      - name: Deploy only the changed service; shared deps via tenant header
        run: |
          helm upgrade --install app ./chart -n "pr-${{ github.event.number }}" \
            --set image.digest="${{ steps.build.outputs.digest }}" \
            --set tenant="pr-${{ github.event.number }}" \
            --wait --timeout 5m
      - name: Comment the URL on the PR
        run: gh pr comment ${{ github.event.number }} --body "Preview: https://pr-${{ github.event.number }}.dev.acme.com"

  teardown:
    if: github.event.action == 'closed'
    runs-on: ubuntu-latest
    steps:
      - run: kubectl delete namespace "pr-${{ github.event.number }}" --ignore-not-found
```

```text
A reaper CronJob deletes namespaces past their TTL label, so a forgotten
environment cannot outlive its purpose. This is the control that keeps the bill honest.
```

## Interview tips

- Name data seeding, dependency handling, and cost as the three hard parts - that structure is the answer.
- Mandatory TTL plus a reaper is the operational detail that shows you have run this at scale.
- Expect: "does this replace staging?" - mostly for feature verification; keep a persistent environment for load and migration rehearsals, and rely on canaries in production.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure Terraform code for multiple environments and providers?]] (`#422`): [How do you structure Terraform code for multiple environments and providers?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [[How do you write and structure a reusable Terraform module?]] (`#463`): [How do you write and structure a reusable Terraform module?](../infrastructure-as-code/how-do-you-write-and-structure-a-reusable-terraform-module.md)
- [[What is Infrastructure as Code?]] (`#26`): [What is Infrastructure as Code?](../infrastructure-as-code/what-is-infrastructure-as-code.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
