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

**Composition is the real feature.** A platform team defines a Composite Resource Definition (the developer-facing API) and a Composition (how it expands into managed resources), so an application team writes 12 lines requesting a database and receives an encrypted, backed-up, correctly-networked instance with credentials delivered as a Kubernetes Secret. That is the same golden-path idea as a Terraform module, but consumable from a manifest in the app's own GitOps repository, with no pipeline permissions to grant.

**Continuous reconciliation cuts both ways.** Manual console changes are reverted automatically, which is excellent for compliance. It also means a mistaken change to a Composition propagates to every claim immediately, without a plan to review - so Compositions need the same rigour as production code: versioned, tested in a staging control plane, and rolled out deliberately. Deletion policies deserve particular care: an accidentally deleted claim can delete a production database, so `deletionPolicy: Orphan` plus protection on the resource is standard.

**The control plane becomes critical infrastructure.** Your Kubernetes cluster is now the thing that provisions and repairs cloud resources. It needs high availability, backups of etcd, upgrade discipline, and its own monitoring - a dedicated management cluster rather than a workload cluster. That operational commitment is the honest cost of the model.

**Where each fits.** Terraform for foundational infrastructure (organisations, networks, the control plane itself) and anywhere you want a reviewed plan gate. Crossplane for the self-service layer application teams consume, especially where GitOps is already the deployment model. Many teams run both, and that hybrid - Terraform for foundation, Crossplane for the developer-facing API - is a defensible and common answer.

**Alternatives to name:** cloud-native operators (AWS Controllers for Kubernetes, Azure Service Operator, GCP Config Connector) give reconciliation without Crossplane's composition layer, and Terraform-based self-service platforms (Terraform Stacks, Atlantis, Spacelift, Env0) provide golden paths while keeping the plan gate.

## Example

```yaml
# Platform team publishes the API (XRD) - the developer contract
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresinstances.platform.acme.com
spec:
  group: platform.acme.com
  names: { kind: XPostgresInstance, plural: xpostgresinstances }
  claimNames: { kind: PostgresInstance, plural: postgresinstances }
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
  writeConnectionSecretToRef:
    name: checkout-db-conn # credentials appear as a Secret, no ticket
```

## Interview tips

- Frame it as reconciliation plus a self-service API versus a reviewed plan - that captures the real difference.
- Raise the risks yourself: weak preview, deletion propagation, and the control plane becoming critical infrastructure.
- Expect: "would you replace Terraform with it?" - usually no; Terraform for foundation, Crossplane for the developer-facing layer.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure Terraform code for multiple environments and providers?]] (`#422`): [How do you structure Terraform code for multiple environments and providers?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [[How do you write and structure a reusable Terraform module?]] (`#463`): [How do you write and structure a reusable Terraform module?](../infrastructure-as-code/how-do-you-write-and-structure-a-reusable-terraform-module.md)
- [[What is Infrastructure as Code?]] (`#26`): [What is Infrastructure as Code?](../infrastructure-as-code/what-is-infrastructure-as-code.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
