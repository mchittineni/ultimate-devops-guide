---
title: "When do you choose CloudFormation, CDK, or Terraform on AWS?"
id: 198
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# When do you choose CloudFormation, CDK, or Terraform on AWS?

**Short answer:** Terraform when you manage more than AWS or want one workflow across providers; CDK when your team is strongest in a programming language and wants abstraction over CloudFormation; raw CloudFormation when you need zero extra tooling, AWS-managed state, or you are shipping Service Catalog products. All three are defensible - the wrong answer is using more than one for the same resources.

## Detail

| Dimension     | CloudFormation                      | CDK                                | Terraform                            |
| ------------- | ----------------------------------- | ---------------------------------- | ------------------------------------ |
| Language      | YAML/JSON                           | TypeScript, Python, Java, Go, .NET | HCL                                  |
| State         | managed by AWS                      | managed by AWS (synthesises CFN)   | you own it (S3 + lock)               |
| Scope         | AWS only                            | AWS only (CDKTF exists separately) | multi-provider                       |
| Drift/preview | drift detection, change sets        | change sets via `cdk diff`         | `terraform plan` (best of the three) |
| New services  | usually first                       | follows CloudFormation coverage    | provider lag, sometimes days–weeks   |
| Failure mode  | rollback, occasionally stuck stacks | same as CloudFormation             | partial apply, state repair          |

**CDK's real advantage is abstraction, not the language.** Constructs let a platform team publish an opinionated, reviewed `SecureBucket` or `StandardService` that encodes tagging, encryption, logging, and alarms, so application teams get compliant infrastructure by default. Its costs are a synth step, a nested-stack model that can be hard to debug, and the ease of writing imperative logic that makes the resulting infrastructure difficult to reason about.

**Terraform's advantage is the plan and the ecosystem.** `terraform plan` is the clearest preview of the three and underpins policy-as-code gates; providers cover AWS plus Datadog, GitHub, Kubernetes, and the rest of the toolchain in one graph. Its costs are state management (remote backend, locking, blast radius of a corrupted state file) and the licence change in 2023 that moved Terraform to BUSL and produced the OpenTofu fork - a question worth being able to discuss neutrally.

**CloudFormation's advantage is that it is the substrate.** No state to manage, native rollback, StackSets for multi-account deployment, and support for new services on launch day. It is verbose, and loops and conditionals are painful, which is exactly the gap CDK fills.

**What actually matters more than the choice:** modules or constructs reviewed by a platform team; a remote backend with locking and per-environment isolation; plan output posted to the pull request; policy-as-code over the plan; and no manual console changes. A team with Terraform and no plan gate is worse off than a team with CloudFormation and a disciplined pipeline.

**Migration is possible in both directions** - Terraform's `import` blocks, CloudFormation's resource import, and CDK's `CfnInclude` - but it is real work. The strongest interview answer names the criteria and then says which one you would standardise on and why, rather than describing all three as equally good.

## Example

```hcl
# Terraform: remote state with locking and a plan gate is the part that matters
terraform {
  required_version = "~> 1.9"
  backend "s3" {
    bucket       = "acme-tfstate-prod"
    key          = "checkout/terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true # S3 native locking; no DynamoDB table required
  }
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.70" }
  }
}
```

```typescript
// CDK: the value is a reviewed construct that makes the compliant path the default
export class SecureBucket extends Construct {
  public readonly bucket: s3.Bucket;
  constructor(scope: Construct, id: string, props?: { retentionDays?: number }) {
    super(scope, id);
    this.bucket = new s3.Bucket(this, "Bucket", {
      encryption: s3.BucketEncryption.KMS_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      versioned: true,
      serverAccessLogsPrefix: "access-logs/",
      lifecycleRules: [{ expiration: Duration.days(props?.retentionDays ?? 365) }],
    });
  }
}
```

## Interview tips

- Give selection criteria, then commit to a recommendation - "it depends" without a conclusion is the weak answer.
- Mention the BUSL licence change and OpenTofu factually; interviewers use it to see whether you follow the ecosystem.
- Expect: "how do you stop console changes?" - drift detection, plan gates in CI, and IAM that denies humans write access in production.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the different types of cloud services?]] (`#25`): [What are the different types of cloud services?](../cloud-platforms/what-are-the-different-types-of-cloud-services.md)
- [[How do you choose a cloud provider for a new workload?]] (`#281`): [How do you choose a cloud provider for a new workload?](../cloud-platforms/how-do-you-choose-a-cloud-provider-for-a-new-workload.md)
- [[What is a cloud landing zone?]] (`#215`): [What is a cloud landing zone?](../cloud-engineering/what-is-a-cloud-landing-zone.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
