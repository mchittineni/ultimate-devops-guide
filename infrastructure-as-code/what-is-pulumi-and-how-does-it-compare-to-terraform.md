---
title: "What is Pulumi and how does it compare to Terraform?"
id: 761
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
  - pulumi
  - terraform
quiz:
  stem: "How does Pulumi behave at deployment time even though programs are written in TypeScript, Python, or Go?"
  options:
    - "It runs the program imperatively, calling cloud APIs line by line"
    - "The program registers resources to build a desired-state graph, and the Pulumi engine diffs that graph against state and applies only the differences"
    - "It converts the program to CloudFormation and submits it"
    - "It has no state, so every run recreates all resources"
  answer: 2
  explanation: "A Pulumi program is general-purpose code that declares resources. The engine collects them into a desired-state graph, compares it with the stack's state, previews the diff (`pulumi preview`), and applies it (`pulumi up`) - declarative at apply time, like Terraform."
---

# What is Pulumi and how does it compare to Terraform?

**Short answer:** Pulumi is an infrastructure-as-code tool where you write infrastructure in a general-purpose language - TypeScript, Python, Go, C#, Java, or YAML - instead of HCL. The program does not call cloud APIs directly: it **registers resources**, the Pulumi engine builds a desired-state graph, diffs it against the **stack's state**, and shows a preview before applying, so it behaves declaratively like Terraform. The real differences are the language (loops, functions, classes, package managers, and unit tests come for free), **secrets encrypted in state by default**, and the ecosystem: Terraform has the larger community, module registry, and hiring pool; Pulumi can reuse Terraform providers through bridged and dynamically generated providers.

## Detail

### How it works

- **Project and stacks.** A project is the program; a **stack** is one deployed instance of it (`dev`, `staging`, `prod`), each with its own configuration and state.
- **Engine and providers.** The language host runs your program; each `new aws.s3.Bucket(...)` registers a resource with the engine, which calls providers to create, update, or delete. Outputs are `Output<T>` values resolved after creation, which is how dependencies are tracked.
- **State backends.** Pulumi Cloud by default, or self-managed: `pulumi login s3://bucket`, Azure Blob, GCS, or local files. Locking and history come with the backend.
- **Commands.** `pulumi preview` (plan), `pulumi up` (apply), `pulumi refresh` (reconcile state with reality), `pulumi destroy`, `pulumi import`.

### Compared with Terraform

| Area             | Terraform / OpenTofu                                                   | Pulumi                                                                                        |
| ---------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Language         | HCL - constrained, declarative, easy to review                         | TypeScript, Python, Go, C#, Java, YAML                                                        |
| Abstraction      | Modules with variables and outputs                                     | Functions, classes, `ComponentResource`s, distributed as language packages                    |
| Testing          | `terraform test`, Terratest                                            | Unit tests with mocked resources in the language's own test framework, plus integration tests |
| Secrets in state | Plaintext unless avoided (ephemeral/write-only) or OpenTofu encryption | Config secrets and secret outputs encrypted per stack (passphrase, KMS, or Pulumi Cloud key)  |
| Providers        | Largest provider ecosystem                                             | Native providers plus bridged Terraform providers; any Terraform provider can be used         |
| Policy           | Sentinel (HCP), OPA/Conftest                                           | CrossGuard policy packs, OPA                                                                  |
| Embedding        | CLI or HCP Terraform API                                               | Automation API: drive `up`/`preview` from your own code (internal platforms, self-service)    |
| Licence          | Terraform BSL; OpenTofu MPL                                            | Engine and SDKs Apache 2.0; Pulumi Cloud is commercial                                        |

HashiCorp's own general-purpose-language option, **CDK for Terraform (CDKTF)**, was sunset and archived in December 2025, so for "Terraform with real languages" the choice is now essentially Pulumi (or AWS CDK for AWS-only estates).

### Trade-offs to state honestly

- **Power cuts both ways.** A real language allows clean abstractions and also clever, unreviewable infrastructure - network calls, randomness, or environment-dependent logic in the program make previews non-deterministic. Teams need conventions: pure functions, no side effects outside resources.
- **Review.** A plan diff (`pulumi preview --diff`) is the review artefact, just as with Terraform; the code itself can be harder for infrastructure reviewers who do not know the language.
- **Ecosystem and hiring.** More engineers, modules, examples, and third-party tools exist for Terraform. Pulumi narrows the gap by consuming Terraform providers, but not modules.
- **Fit.** Pulumi shines when application developers own their infrastructure in the same language as the app, or when a platform team builds self-service tooling with the Automation API. HCL shines when many teams need a constrained, uniform format that is easy to read.

## Example

```typescript
// index.ts (@pulumi/aws v7) - one private, versioned bucket per environment, via a reusable function
import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const env = pulumi.getStack(); // dev | staging | prod

function privateBucket(name: string): aws.s3.Bucket {
  const bucket = new aws.s3.Bucket(name, { tags: { env, managedBy: "pulumi" } });
  new aws.s3.BucketVersioning(`${name}-versioning`, {
    bucket: bucket.id,
    versioningConfiguration: { status: "Enabled" },
  });
  new aws.s3.BucketPublicAccessBlock(`${name}-pab`, {
    bucket: bucket.id,
    blockPublicAcls: true,
    blockPublicPolicy: true,
    ignorePublicAcls: true,
    restrictPublicBuckets: true,
  });
  return bucket;
}

const artifacts = privateBucket(`artifacts-${env}`);
export const bucketName = artifacts.bucket;
export const apiKey = config.requireSecret("apiKey"); // stays encrypted in state and output
```

```bash
pulumi login s3://acme-pulumi-state            # self-managed backend
pulumi stack init prod --secrets-provider="awskms://alias/pulumi-prod"
pulumi config set aws:region eu-west-1
pulumi config set --secret apiKey "s3cr3t"     # encrypted with the stack's KMS key
pulumi preview --diff                          # the reviewable plan
pulumi up --yes                                # apply
```

## Interview tips

- Correct the misconception first: Pulumi is not imperative scripting - the program declares resources and the engine diffs desired state against state, exactly like Terraform's plan/apply.
- Give the genuine differentiators: real languages and testing, secrets encrypted in state by default, the Automation API, and reuse of Terraform providers.
- Be balanced on the costs: non-deterministic programs, harder review for infrastructure specialists, and a smaller ecosystem and hiring pool than Terraform.
- Mention that CDKTF was archived in December 2025, which makes Pulumi the main multi-cloud "IaC in a programming language" option.
- Likely follow-up: "how would you migrate?" - `pulumi convert --from terraform` for code and `pulumi import` (or referencing Terraform state outputs) for existing resources, one stack at a time. See [what is Terraform](./what-is-terraform.md), [declarative versus imperative IaC](./what-is-the-difference-between-declarative-and-imperative-infrastructure-as-code.md), and [Terraform versus OpenTofu](./what-is-the-difference-between-terraform-and-opentofu.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[What is the difference between mutable and immutable infrastructure in modern deployment patterns?]] (`#586`): [What is the difference between mutable and immutable infrastructure in modern deployment patterns?](../configuration-management/what-is-the-difference-between-mutable-and-immutable-infrastructure-in-modern-deployment-patterns.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
