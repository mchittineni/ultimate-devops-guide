---
title: "What are ephemeral preview environments and how do you manage their lifecycle and cleanup?"
id: 535
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cicd
  - kubernetes
  - preview-environments
  - gitops
quiz:
  stem: "What is the primary risk of implementing ephemeral pull-request environments without an automated reaper mechanism?"
  options:
    - "Git repositories will lock against incoming commits"
    - "Abandoned or idle environments from merged or inactive PRs will accumulate and inflate cloud infrastructure costs"
    - "Developers will be unable to run unit tests locally"
    - "Docker images will automatically delete themselves"
  answer: 2
  explanation: "Without automated cleanup (reapers based on PR closure or TTL timers), forgotten preview environments consume cloud compute, IPs, and databases, leading to high cost waste."
---

# What are ephemeral preview environments and how do you manage their lifecycle and cleanup?

**Short answer:** Ephemeral preview environments are isolated, temporary application environments spun up automatically per pull request and destroyed when the PR closes, enabling realistic testing and stakeholder review before merging.

## Detail

Instead of sharing a static staging environment where developers queue up or overwrite each other's code, ephemeral environments provide dedicated environments (e.g., `https://pr-142.preview.company.com`).

### Lifecycle Workflow

1. **Creation Trigger**: PR opened or updated.
2. **Provisioning**:
   - Provision a dedicated Kubernetes namespace (`preview-pr-142`) or vcluster.
   - Deploy the container built from the PR branch via Helm or ArgoCD ApplicationSets.
   - Configure dynamic Ingress/Gateway routes with automatic TLS certs (`cert-manager`).
   - Seed database using sanitized snapshots, ephemeral DB instances, or transactional rollbacks.
3. **Feedback**: Bot posts preview URL directly into the PR commentary.
4. **Teardown & Cost Control**:
   - Automatically delete namespace on PR close or merge (`github.event.action == 'closed'`).
   - Run a scheduled reaper cronjob to terminate stale environments older than 3 days to avoid cloud bill bloat. The close event is not enough on its own: workflows fail, webhooks get lost, and PRs go idle for weeks, so the reaper is the real guarantee.

### Trade-offs and limits

- **Cost and capacity**: each environment consumes compute, load-balancer or DNS entries, and often a database. Share expensive dependencies (a single shared database server with a schema per PR, or stubs for third-party APIs), scale idle environments to zero, and cap the number of concurrent previews.
- **Fidelity**: a namespace on a shared cluster is not production - no real traffic, smaller data, shared nodes. Previews are for functional review and integration tests, not for performance or capacity testing.
- **Security**: previews built from fork PRs run untrusted code; give them no production credentials, synthetic or sanitised data only, and put them behind SSO so an unreviewed branch is not a public website.
- **Ownership labels**: label every resource with the PR number and an expiry (`preview/pr: "142"`, `preview/expires-at`) so the reaper can find it and cost reports can attribute it.

## Example

```yaml
# .github/workflows/preview.yml - create on open/update, destroy on close
name: preview
on:
  pull_request:
    types: [opened, synchronize, reopened, closed]

permissions:
  contents: read
  id-token: write # OIDC to the cluster's cloud account; no stored kubeconfig

concurrency:
  group: preview-${{ github.event.pull_request.number }}
  cancel-in-progress: false # never cancel a half-finished teardown

jobs:
  deploy:
    if: github.event.action != 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      # (cloud login + kubeconfig step omitted)
      - run: |
          NS=preview-pr-${{ github.event.pull_request.number }}
          kubectl create namespace "$NS" --dry-run=client -o yaml | kubectl apply -f -
          kubectl label namespace "$NS" preview=true --overwrite
          helm upgrade --install app ./chart -n "$NS" \
            --set image.tag=${{ github.event.pull_request.head.sha }} \
            --set ingress.host=pr-${{ github.event.pull_request.number }}.preview.example.com

  teardown:
    if: github.event.action == 'closed'
    runs-on: ubuntu-latest
    steps:
      # (cloud login + kubeconfig step omitted)
      - run: kubectl delete namespace preview-pr-${{ github.event.pull_request.number }} --ignore-not-found
```

```bash
# Nightly reaper: delete preview namespaces older than 3 days, whatever happened to their PR
kubectl get ns -l preview=true -o json \
  | jq -r --arg cutoff "$(date -u -d '3 days ago' +%Y-%m-%dT%H:%M:%SZ)" \
      '.items[] | select(.metadata.creationTimestamp < $cutoff) | .metadata.name' \
  | xargs -r kubectl delete ns
```

## Interview tips

- Describe the full lifecycle - trigger, provision, seed, report the URL, tear down - and stress that teardown has two independent paths: the PR-close event and a TTL reaper.
- Name the isolation choice and its cost: namespace per PR (cheap, shared control plane) versus vcluster or a full cluster (stronger isolation, more cost and startup time).
- Data is the hard part: sanitised snapshots, per-PR schemas, or seeded fixtures - never raw production data.
- Mention security for fork PRs: untrusted code, no production secrets, preview URLs behind authentication.
- Likely follow-up: "how do you keep this affordable?" - scale to zero, shared backing services, a concurrency cap, and labels for cost attribution.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What is Kustomize and how does it achieve overlay configuration without templating?]] (`#630`): [What is Kustomize and how does it achieve overlay configuration without templating?](../devops-tools-and-automation/what-is-kustomize-and-how-does-it-achieve-overlay-configuration-without-templating.md)
- [[What is Crossplane and how does it turn Kubernetes into a universal cloud infrastructure control plane?]] (`#633`): [What is Crossplane and how does it turn Kubernetes into a universal cloud infrastructure control plane?](../devops-tools-and-automation/what-is-crossplane-and-how-does-it-turn-kubernetes-into-a-universal-cloud-infrastructure-control-plane.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
