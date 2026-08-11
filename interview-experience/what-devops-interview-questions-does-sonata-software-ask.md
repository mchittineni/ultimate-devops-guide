---
title: "What DevOps interview questions does Sonata Software ask?"
id: 379
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - sonata-software
  - azure-engineering
  - aws-engineering
  - infrastructure-as-code
  - kubernetes
  - serverless-architecture
  - api-gateway-and-service-mesh
  - scripting-and-automation
---

# What DevOps interview questions does Sonata Software ask?

## Questions

### Round set 1 — Azure, AKS, and Terraform (5 YOE)

- **What is the difference between Application Gateway and Front Door?**
- **How do you protect your endpoints in AKS, and what networking model are you using in AKS?**
- **How do you do cost optimisation in the cloud?**
- **How do you block a particular domain in Application Gateway?**
- **How would you write a Terraform module, and how do you upgrade a module version?**
- **Share your screen and write out your Terraform directory structure.**
- **How do you monitor whether Pods go down?**
- **Which metric do you use when CPU or memory on a VM goes beyond 75%?**
- **Where do you store the Application Gateway TLS/SSL certificate?**
- **How long would it take you to write the IaC and deploy an App Service?**
- **How do you build a CI/CD pipeline in Azure DevOps?**
- **Your SQL database CPU goes beyond 75%. How do you scale it up?**
- **Have you used Terraform Cloud?**
- **Do you use Helm charts for AKS deployments?**

### Round set 2 — AWS, Terraform, GitLab, and scripting (6+ YOE)

**AWS — serverless and API Gateway**

- **Which AWS services have you worked on?**
- **What is a cold start in Lambda?**
- **Have you worked with API Gateway, and what is the difference between REST APIs and WebSocket APIs in it?**
- **How do you protect an API Gateway?**

**AWS — networking and IAM**

- **What is the difference between a NAT gateway and an internet gateway?**
- **If a user has both an explicit deny and an allow policy in IAM, what happens?**
- **What is the difference between a managed policy and an inline policy?**

**AWS — secrets**

- **How do you retrieve secrets from Secrets Manager using Python?**
- **How do you protect the secrets held in Secrets Manager, and how are they encrypted?**

**AWS — compute, scaling, and databases**

- **You need EC2 instances to be configured automatically, or to replace themselves when they fail. How do you implement that?**
- **Have you worked with Auto Scaling, what is its use case, and will it scale up automatically — how do you set that up?**
- **You have EC2 instances running web servers and need to deploy updates with minimal downtime. How do you approach it?**
- **What is the difference between traditional RDS and Aurora, and how does Aurora handle automatic backups?**
- **Have you worked with AppConfig?**

**Terraform**

- **Have you worked with Terraform?**
- **You created an S3 bucket with Terraform and want to change the bucket name. Is that possible, and how would you do it?**
- **What is a `data` block in Terraform?**
- **How do you handle multiple environments in Terraform?**
- **What are modules in Terraform?**

**GitLab CI/CD**

- **Have you worked with GitLab, and what are `rules` in GitLab CI?**

**Scripting and Python**

- **Which scripting language have you used?**
- **What is the difference between a single `&` and a double `&&` in shell scripting?**
- **What does the `search` keyword do in Python?**
- **What is the difference between a shallow copy and a deep copy in Python?**

## Example

```text
Sonata Software — DevOps Engineer, two reported rounds (~38 questions)

  SET 1  Azure / AKS / Terraform (5 YOE)     14   App Gateway vs Front Door,
                                                  block a domain, where the TLS
                                                  cert lives, screen-share your
                                                  Terraform structure, scale a
                                                  SQL DB at 75% CPU
  SET 2  AWS / TF / GitLab / scripting        24   Lambda cold start, REST vs
                                                  WebSocket API, explicit deny,
                                                  rename an S3 bucket, GitLab
                                                  rules, & vs &&, shallow vs
                                                  deep copy

TWO CLOUDS, TWO STYLES
  Round 1 is Azure and asks you to screen-share and write. Round 2 is AWS and
  asks precise factual questions with definite answers. Prepare differently
  for each.
```

## Interview tips

- The S3 bucket rename question has a definite answer that catches people out: bucket names are **immutable**, so you cannot rename one. Terraform will plan a destroy and create — which fails if the bucket is non-empty, and even when it succeeds you have lost the data and the old name may be unavailable for reuse. So the real answer is: create the new bucket, copy the objects across with `aws s3 sync`, repoint consumers, then remove the old one — and if you only want Terraform to stop managing the old bucket, `terraform state rm`. Saying "the resource is immutable, so this is a migration, not a rename" is what wins it.
- The explicit-deny question is the single most important IAM fact: an explicit `Deny` **always wins**, regardless of any allow, and no matter where it appears — identity policy, resource policy, permission boundary, or service control policy. Then give the full evaluation order, because that is the natural follow-up: explicit deny, then SCPs, then permission boundaries, then resource-based and identity-based allows, with an implicit deny by default if nothing allows. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md).
- Managed versus inline policy: a managed policy is a standalone, reusable, versioned object attachable to many identities — AWS-managed or customer-managed; an inline policy is embedded in a single user, group, or role and is deleted with it. Say the recommendation and the reason: prefer customer-managed policies because they are reusable, auditable, and can be rolled back to a previous version, and use inline only when you need a guaranteed one-to-one relationship that cannot be attached elsewhere.
- Lambda cold start should be answered as a mechanism plus mitigations: a cold start is the time to create an execution environment, download and initialise the runtime and your code, and run any initialisation outside the handler — so it hits the first invocation and any scale-out. Mitigations, best first: provisioned concurrency for predictable latency, SnapStart for Java, a smaller deployment package with fewer dependencies, moving SDK client creation and connection setup outside the handler so it is reused, and avoiding VPC attachment unless you need private resources. Mention that VPC cold starts used to be far worse before Hyperplane ENIs, and that a lighter runtime helps.
- REST versus WebSocket APIs in API Gateway is a protocol distinction: REST (and HTTP APIs) are request-response and stateless, each call independent; WebSocket APIs hold a persistent bidirectional connection with `$connect`, `$disconnect`, and route keys, so the server can push to clients — which is what you use for chat, live dashboards, or notifications. Add that HTTP APIs are the cheaper, faster successor to REST APIs but with fewer features, so the three-way comparison is worth naming. For protecting an API Gateway: authorisers (IAM, Cognito, or Lambda), usage plans and API keys with throttling and quotas, WAF on the edge, resource policies restricting source VPC or IP, mutual TLS for partner APIs, and private endpoints so it is not internet-reachable at all.
- The self-healing EC2 question has a specific expected answer: an Auto Scaling group with health checks — ELB health checks in addition to EC2 status checks, since an instance can be "running" while the application is dead — so a failed instance is terminated and replaced automatically, with a launch template plus `user_data` or a baked AMI providing the automatic configuration. Then the minimal-downtime deployment half: an ASG instance-refresh with a minimum healthy percentage, or blue-green with two target groups and a weighted listener, plus deregistration delay for connection draining. Naming ELB health checks as distinct from EC2 status checks is the differentiator. See [how auto-scaling groups and load balancers work together](../aws-engineering/how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md).
- RDS versus Aurora needs the architectural difference, not a feature list: Aurora separates compute from a distributed storage layer that keeps six copies across three availability zones, so replicas share the same storage rather than replicating logically — which gives faster failover, up to fifteen low-lag readers, and storage that grows automatically. Backups are continuous to S3 with point-in-time recovery and no performance penalty, because they happen at the storage layer rather than as a snapshot of the instance. That last point is the answer to the backup half. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- Application Gateway versus Front Door is a scope question: Application Gateway is a _regional_ layer-7 load balancer inside your VNet with WAF, path and host routing, and TLS termination; Front Door is a _global_ edge service with anycast entry, CDN caching, global failover, and WAF at the edge. Say that they compose — Front Door globally in front of a regional Application Gateway — and that the AWS analogues are ALB and CloudFront plus Global Accelerator. For blocking a domain in Application Gateway, the honest answer is that Application Gateway controls _inbound_ traffic, so blocking a domain a client requests is a WAF custom rule matching the `Host` header; blocking an _outbound_ destination domain is Azure Firewall's FQDN filtering, not Application Gateway. Distinguishing inbound from outbound is the point.
- "Where do you store the Application Gateway TLS certificate?" has a precise best answer: as a certificate in Azure Key Vault, referenced by the listener through a user-assigned managed identity, using the **versionless** secret identifier so a rotated certificate is picked up automatically. Say that a version-pinned reference is exactly why certificates "expire despite being renewed", and that uploading a `.pfx` directly to the gateway means you must remember to replace it manually. See [what SSL/TLS is](../network-security/what-is-ssl-tls.md).
- The two 75% questions are different problems, so answer them differently. For a VM, memory is not a default platform metric — you need the Azure Monitor agent with a data collection rule to gather the memory performance counter, then a metric alert with an action group; CPU is available natively. For the SQL database at 75% CPU, the answer is to scale the service tier or vCPU count — which for a single database is an online operation with a brief failover — or move to serverless or Hyperscale, add read replicas to offload reads, and first check whether a missing index or a bad query plan is the real cause. Saying "I would look at the top queries before paying for more compute" is the answer a senior engineer gives.
- On monitoring Pods going down, name the signals rather than the tool: `kube_pod_container_status_restarts_total` and Pod phase from kube-state-metrics, alerting on restart rate and on `Ready` replicas being below the desired count — plus the point that a Pod restarting is normal and what matters is _frequency_ and whether the Service still has healthy endpoints. See [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md).
- The Terraform module questions want the interface and the versioning discipline: inputs, outputs, a `source` and a pinned `version`, and upgrading means bumping that version constraint, running `terraform init -upgrade`, and reviewing the plan — never a floating version, because a module upgrade can plan a destroy. For the screen-share structure question, be ready to type a real layout: `modules/` for reusable components, `envs/dev|stage|prod` as root modules each with their own backend and `tfvars`, plus `versions.tf` pinning provider and Terraform versions. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md) and [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The scripting questions have exact answers worth having ready. `&` runs a command in the background; `&&` runs the next command only if the previous one exited zero — and mention `&&` versus `;` versus `||` as the full set. In Python, `re.search` scans the whole string for the first match anywhere, in contrast to `re.match` which anchors at the start and `re.fullmatch` which must match entirely. Shallow copy (`copy.copy`, or a slice, or `dict()`) creates a new outer object whose elements are still references to the same nested objects, so mutating a nested list affects both; deep copy (`copy.deepcopy`) recursively copies everything. Give the nested-list example — that is what makes the answer concrete. See [what you use Python for as a DevOps engineer](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md).
- GitLab `rules` replaced `only`/`except` and control whether a job is created, using `if`, `changes`, and `exists` conditions with `when: manual`, `never`, `always`, or `on_success`, plus `allow_failure`. Say that `rules` are evaluated in order and the first match wins, and that `changes` is how you build a monorepo pipeline that only runs jobs for the services that actually changed. See [what GitLab CI is](../cicd/what-is-gitlab-ci.md).
- Retrieving a secret in Python is `boto3.client("secretsmanager").get_secret_value(SecretId=...)`, parsing `SecretString` as JSON — and the details that matter are caching the value rather than calling on every request (the AWS Secrets Manager caching library or the Lambda extension), using an IAM role rather than keys, and that protection comes from KMS encryption plus a resource policy plus rotation with a Lambda rotation function. Say that a secret fetched into memory should never be logged. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Site Reliability Engineering?]] (`#96`): [What is Site Reliability Engineering?](../site-reliability-engineering/what-is-site-reliability-engineering.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
