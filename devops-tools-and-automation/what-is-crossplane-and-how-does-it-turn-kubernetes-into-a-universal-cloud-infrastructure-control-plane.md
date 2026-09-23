---
title: "What is Crossplane and how does it turn Kubernetes into a universal cloud infrastructure control plane?"
id: 633
category: "DevOps Tools and Automation"
difficulty: "Advanced"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
  - crossplane
  - kubernetes
  - iac
  - control-plane
  - gitops
quiz:
  stem: "What is the primary difference in execution model between Crossplane and traditional Terraform?"
  options:
    - "Crossplane can only deploy Docker containers, not cloud resources"
    - "Terraform runs on-demand batch workflows in CI/CD, while Crossplane runs continuous active reconciliation loops inside the Kubernetes control plane"
    - "Crossplane does not support AWS or GCP"
    - "Terraform does not support state files"
  answer: 2
  explanation: "Terraform is a CLI tool that executes when triggered. Crossplane runs inside Kubernetes as an active controller, continuously observing live cloud infrastructure and reconciling drift 24/7."
---

# What is Crossplane and how does it turn Kubernetes into a universal cloud infrastructure control plane?

**Short answer:** Crossplane extends Kubernetes with custom resources for cloud services (RDS, S3, Azure SQL) and with platform-defined abstractions, so teams manage infrastructure declaratively through the Kubernetes API - with its RBAC, GitOps tooling, and continuous reconciliation - rather than through one-off Terraform runs.

## Detail

Crossplane runs as controllers inside a Kubernetes cluster that acts as a **control plane**. It has two layers:

- **Providers** install **managed resources** (MRs) - one CRD per cloud API object, such as `Bucket`, `RDSInstance`, `VirtualNetwork`. Each MR is reconciled continuously: the provider observes the real resource and corrects drift. Providers authenticate with a `ProviderConfig` (ideally workload identity such as IRSA/EKS Pod Identity, not static keys).
- **Composition** lets the platform team define its own API. A **CompositeResourceDefinition (XRD)** declares a new kind, such as `PostgresDatabase` with a `size` field, and a **Composition** says what that kind expands into - an RDS instance, a subnet group, a security group, a secret. Compositions are a pipeline of **composition functions** (patch-and-transform, KCL, Go templating, Python) rather than the older inline patch-and-transform mode.

### What changed in Crossplane v2

Crossplane v2 (August 2025) simplified the model: composite resources (XRs) and managed resources are now **namespaced** by default, so a developer creates the XR directly in their own namespace and ordinary Kubernetes RBAC governs it. **Claims are gone** for v2-style XRs (legacy cluster-scoped v1 XRs keep them), compositions can include any Kubernetes resource - not just cloud resources - and XRs no longer carry native connection details, so a composition writes its own connection `Secret`. Existing v1 resources keep working after the upgrade.

### How it differs from Terraform

|           | Terraform / OpenTofu                                         | Crossplane                                                                  |
| --------- | ------------------------------------------------------------ | --------------------------------------------------------------------------- |
| Execution | A CLI run triggered by a person or pipeline (`plan`/`apply`) | Controllers reconciling continuously                                        |
| State     | A state file in a backend                                    | The Kubernetes API (etcd) plus the cloud itself                             |
| Drift     | Detected on the next plan                                    | Corrected on the next reconcile (polling, typically every minute or so)     |
| Interface | HCL modules                                                  | Kubernetes APIs you design (XRDs), usable from `kubectl`, GitOps, Backstage |
| Preview   | `plan` shows the diff before applying                        | No equivalent of a reviewed plan; changes apply when the object changes     |

**Trade-offs.** Crossplane makes the cluster a critical dependency - lose the control plane and you lose the ability to change infrastructure (the cloud resources keep running). There is no `plan` step, so review happens on the manifest, not on the resulting diff. Debugging spans XR, composition function, and MR status conditions. Provider CRDs are numerous and heavy on the API server (install only the provider families you need). And continuous reconciliation cuts both ways: a manual emergency change in the console will be reverted.

## Example

```yaml
# Platform team: a namespaced API for developers (Crossplane v2).
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata: { name: postgresdatabases.platform.acme.com }
spec:
  scope: Namespaced
  group: platform.acme.com
  names: { kind: PostgresDatabase, plural: postgresdatabases }
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                storageGB: { type: integer, minimum: 20, maximum: 500 }
              required: [storageGB]
---
# Developer: request a database in their own namespace - no claim needed in v2.
apiVersion: platform.acme.com/v1alpha1
kind: PostgresDatabase
metadata: { name: orders-db, namespace: team-orders }
spec:
  storageGB: 50
```

```bash
# Trace a request from the XR down to the cloud resources it composed.
kubectl get postgresdatabase orders-db -n team-orders
crossplane beta trace postgresdatabase orders-db -n team-orders
kubectl get managed -n team-orders       # the RDS instance, subnet group, ... and their status
```

## Interview tips

- Explain the two layers: providers with managed resources, and composition (XRDs plus Compositions built from functions) for platform APIs.
- Contrast the execution model with Terraform: continuous reconciliation versus triggered runs - and admit the lack of a `plan` step.
- Mention Crossplane v2: namespaced XRs and MRs, claims removed for new XRs, function pipelines.
- Name the operational risk: the control-plane cluster becomes critical infrastructure and must be backed up and protected.
- A good answer ends with when to use each - many teams keep Terraform/OpenTofu for foundations and use Crossplane for self-service resources.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
