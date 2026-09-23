---
title: "What is Crossplane and how does it compare to Terraform?"
id: 226
category: "Platform Engineering"
difficulty: "Advanced"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# What is Crossplane and how does it compare to Terraform?

**Short answer:** Crossplane turns cloud infrastructure into Kubernetes resources reconciled continuously by controllers, and lets a platform team publish composite abstractions (a `PostgresInstance` that expands into a real database, subnet group, secret, and firewall rule) as custom resources. Terraform runs as a batch job producing a plan you review and apply. Crossplane's advantage is continuous reconciliation and a native self-service API; Terraform's is maturity, ecosystem, and the trustworthiness of `plan`.

## Detail

| Dimension        | Terraform                            | Crossplane                                   |
| ---------------- | ------------------------------------ | -------------------------------------------- |
| Execution        | imperative run of a declarative plan | continuous control-loop reconciliation       |
| Drift            | detected when you next plan          | corrected automatically, always              |
| Preview          | `terraform plan` - strong            | weak; you observe reconciliation             |
| State            | state file you own                   | Kubernetes etcd + provider status            |
| Self-service API | modules invoked in a pipeline        | CRDs consumed like any Kubernetes object     |
| Ecosystem        | vast provider and module ecosystem   | growing; providers generated from cloud APIs |
| Prerequisite     | a runner and a backend               | a Kubernetes cluster you must keep healthy   |

**Composition is the real feature.** A platform team defines a Composite Resource Definition (the developer-facing API) and a Composition (a pipeline of composition functions describing how it expands into managed resources), so an application team writes a dozen lines requesting a database and receives an encrypted, backed-up, correctly-networked instance with credentials delivered as a Kubernetes Secret. Since Crossplane v2 (August 2025) these composite resources are namespaced, so developers create them directly in their own namespace; the older cluster-scoped XR plus namespaced _claim_ pattern is legacy, and the composition itself writes the connection Secret. That is the same golden-path idea as a Terraform module, but consumable from a manifest in the app's own GitOps repository, with no pipeline permissions to grant.

**Continuous reconciliation cuts both ways.** Manual console changes are reverted automatically, which is excellent for compliance. It also means a mistaken change to a Composition propagates to every composite resource immediately, without a plan to review - so Compositions need the same rigour as production code: versioned (Composition revisions let you pin or stage updates), tested in a staging control plane, and rolled out deliberately. Deletion policies deserve particular care: an accidentally deleted composite resource can delete a production database, so a no-delete policy on the managed resources (`deletionPolicy: Orphan`, or management policies that omit `Delete`) plus protection on the resource is standard.

**The control plane becomes critical infrastructure.** Your Kubernetes cluster is now the thing that provisions and repairs cloud resources. It needs high availability, backups of etcd, upgrade discipline, and its own monitoring - a dedicated management cluster rather than a workload cluster. That operational commitment is the honest cost of the model.

**Where each fits.** Terraform for foundational infrastructure (organisations, networks, the control plane itself) and anywhere you want a reviewed plan gate. Crossplane for the self-service layer application teams consume, especially where GitOps is already the deployment model. Many teams run both, and that hybrid - Terraform for foundation, Crossplane for the developer-facing API - is a defensible and common answer.

**Alternatives to name:** cloud-native operators (AWS Controllers for Kubernetes, Azure Service Operator, GCP Config Connector) give reconciliation without Crossplane's composition layer, and Terraform-based self-service platforms (Terraform Stacks, Atlantis, Spacelift, Env0) provide golden paths while keeping the plan gate. Note also that Terraform has been under the Business Source License since 2023; OpenTofu is the MPL-licensed, CLI-compatible fork, which matters to some organisations' tooling policies.

## Example

```yaml
# Platform team publishes the API (XRD) - the developer contract (Crossplane v2)
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: postgresinstances.platform.acme.com
spec:
  scope: Namespaced # v2: developers create the XR in their own namespace, no claim
  group: platform.acme.com
  names: { kind: PostgresInstance, plural: postgresinstances }
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
                size: { type: string, enum: [small, medium, large] }
                region: { type: string }
              required: [size, region]
```

```yaml
# Application team consumes it - 10 lines, in their own GitOps repo
apiVersion: platform.acme.com/v1alpha1
kind: PostgresInstance
metadata:
  name: checkout-db
  namespace: team-payments
spec:
  size: small
  region: eu-west-1
# The Composition writes the credentials to a Secret (e.g. checkout-db-conn) in this
# namespace - no ticket, no pipeline permissions.
```

## Interview tips

- Frame it as reconciliation plus a self-service API versus a reviewed plan - that captures the real difference.
- Raise the risks yourself: weak preview, deletion propagation, and the control plane becoming critical infrastructure.
- Mention Crossplane v2 (namespaced composite resources, claims removed for new APIs, function pipelines) so the answer does not sound dated.
- Expect: "would you replace Terraform with it?" - usually no; Terraform for foundation, Crossplane for the developer-facing layer.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Backstage and how does it build an Internal Developer Portal (IDP) with software catalogs?]] (`#634`): [What is Backstage and how does it build an Internal Developer Portal (IDP) with software catalogs?](../devops-tools-and-automation/what-is-backstage-and-how-does-it-build-an-internal-developer-portal-idp-with-software-catalogs.md)
- [[How do you structure Terraform code for multiple environments and providers?]] (`#422`): [How do you structure Terraform code for multiple environments and providers?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [[How do you write and structure a reusable Terraform module?]] (`#463`): [How do you write and structure a reusable Terraform module?](../infrastructure-as-code/how-do-you-write-and-structure-a-reusable-terraform-module.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
