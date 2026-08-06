---
title: "What are Terraform providers?"
id: 30
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
---

# What are Terraform providers?

**Short answer:** A provider is a plugin that teaches Terraform how to talk to an API — AWS, Azure, Kubernetes, GitHub, Datadog — exposing that platform's resources and data sources to HCL.

## Detail

Providers are what make Terraform universal. The core binary understands configuration, dependency graphs, and state; every actual API call is made by a provider. There are thousands in the public registry, plus the ability to write your own with the Terraform Plugin Framework.

What a provider supplies:

- **Resources** — things Terraform creates and owns (`aws_instance`, `kubernetes_deployment`).
- **Data sources** — read-only lookups of things it does not own (`aws_ami`, `aws_caller_identity`).
- **Provider configuration** — region, credentials, endpoints, default tags.

**Aliases** let you configure the same provider more than once — multiple regions or multiple accounts in a single configuration — and select one per resource with `provider = aws.eu`.

**Version constraints** matter. Providers evolve independently of Terraform; pin with `~>` and commit the `.terraform.lock.hcl` lock file so every engineer and every CI run resolves identical versions and checksums.

Authentication should come from the environment — an assumed role, an OIDC token from CI, or a cloud SDK credential chain — never hardcoded keys in the provider block.

## Example

```hcl
terraform {
  required_providers {
    aws        = { source = "hashicorp/aws",        version = "~> 5.60" }
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.32" }
  }
}

provider "aws" {
  region = "eu-west-1"
  default_tags { tags = { ManagedBy = "terraform", Environment = var.environment } }
}

provider "aws" {
  alias  = "us"
  region = "us-east-1"        # e.g. ACM certificates for CloudFront
}

resource "aws_acm_certificate" "cdn" {
  provider          = aws.us
  domain_name       = "www.example.com"
  validation_method = "DNS"
}
```

## Interview tips

- Provider aliases for multi-region/multi-account work is a frequent practical follow-up.
- Explain the lock file: it pins provider versions _and_ checksums, and belongs in version control.
- `default_tags` on the AWS provider is a neat answer to "how do you enforce tagging?"

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
