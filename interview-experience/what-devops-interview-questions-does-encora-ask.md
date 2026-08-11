---
title: "What DevOps interview questions does Encora ask?"
id: 332
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - encora
  - infrastructure-as-code
  - kubernetes
  - azure-engineering
  - container-orchestration-advanced
  - devsecops
  - network-security
  - version-control
---

# What DevOps interview questions does Encora ask?

## Questions

**Terraform**

- **What is the Terraform lifecycle?**
- **I created a resource manually. How do you bring it under Terraform management?**
- **What is the difference between `for_each` and `count`? Give examples.**
- **How do you create a Terraform module, and how do you reference it?**
- **Given the range `10.0.0.0/16`, I want `/21` subnets carved out of it. How do you achieve that in Terraform, and how do you use `locals` to do it?**

**Kubernetes**

- **Explain the architecture of Kubernetes.**
- **What are CSI drivers?**
- **What is a CNI plugin?**
- **What is the difference between a DaemonSet and a StatefulSet?**
- **A Pod is in `CrashLoopBackOff`. What steps do you follow to investigate further?**

**Helm**

- **What is the difference between `helm template` and `helm install`?**
- **What is the `_helpers.tpl` file in a Helm chart for?**
- **Which files exist inside a Helm chart?**

**Azure security and certificates**

- **What is a service principal in Azure? Give an example of using one.**
- **How do you rotate secrets in Key Vault, and how do you deploy a `.pfx` certificate on Application Gateway alongside the ingress controller in AKS?**

**Security and traffic design**

- **You have multiple microservices and multiple websites, and you need to secure them. How do you approach that?**
- **There is a backend API and you need secure service-to-service communication with it. How do you implement that?**
- **How do you handle a traffic spike after a new product launches on a web application?**

**Delivery process**

- **What branching strategies do you use, and what is your pipeline creation mechanism?**

## Example

```text
Encora — DevOps Engineer (7 YOE), reported round
19 questions

  Terraform                   5   lifecycle, import a manual resource,
                                  for_each vs count, modules, /16 -> /21
                                  subnetting with locals
  Kubernetes                  5   architecture, CSI, CNI, DaemonSet vs
                                  StatefulSet, CrashLoopBackOff
  Helm                        3   template vs install, _helpers.tpl,
                                  chart file layout
  Azure security              2   service principal, Key Vault rotation +
                                  .pfx on Application Gateway with AKS ingress
  Security / traffic design   3   securing many microservices, secure
                                  service-to-service, launch traffic spike
  Delivery process            1   branching + pipeline mechanism

THE QUESTION TO PREPARE HARDEST
  The /16 -> /21 subnetting with locals. It is the only question that
  requires you to produce working HCL with a function most people have to
  look up.
```

```hcl
# The subnetting question. cidrsubnet() with 5 extra bits turns a /16 into
# /21 blocks; locals + for_each keep it declarative instead of hand-written.
locals {
  vpc_cidr = "10.0.0.0/16"
  # /21 is 5 bits beyond /16 -> 32 possible subnets, take the first four.
  subnets = {
    for i in range(4) :
    "subnet-${i}" => cidrsubnet(local.vpc_cidr, 5, i)
  }
  # => 10.0.0.0/21, 10.0.8.0/21, 10.0.16.0/21, 10.0.24.0/21
}

resource "aws_subnet" "this" {
  for_each          = local.subnets
  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = data.aws_availability_zones.available.names[
    index(keys(local.subnets), each.key) % 3
  ]
  tags = { Name = each.key }
}
```

## Interview tips

- For the subnetting question, the function you need is `cidrsubnet(prefix, newbits, netnum)`, and the arithmetic is the part to say out loud: going from `/16` to `/21` adds 5 bits, so `newbits` is 5 and you get 32 possible subnets. Then use a `locals` block with a `for` expression to generate the map and `for_each` over it, so adding a subnet is a number change rather than a copy-paste. Mention `cidrsubnets()` as the plural variant when you want several different sizes from one prefix.
- `for_each` versus `count` has a preferred answer and a reason. `count` gives you a list indexed by position, so removing the middle element re-indexes everything after it and Terraform destroys and recreates resources that did not change. `for_each` keys resources by a stable string, so removals only affect that key. Say "use `for_each` unless you genuinely need a simple numeric replica count" — that is the recommendation interviewers want. Give the address difference too: `aws_subnet.this[0]` versus `aws_subnet.this["subnet-a"]`.
- The "Terraform lifecycle" question is ambiguous, so cover both readings in two sentences. The workflow lifecycle is `init`, `validate`, `plan`, `apply`, `destroy`. The `lifecycle` meta-argument block is separate and holds `create_before_destroy`, `prevent_destroy`, `ignore_changes`, and `replace_triggered_by`. Answering both and saying which you think they mean is stronger than picking one.
- `helm template` versus `helm install` is a good discriminator: `template` renders the chart locally to YAML and never touches the cluster or creates a release, which is what you use in CI to diff or to feed into a GitOps repository; `install` renders it _and_ submits it to the API server, recording a release with revision history so `helm rollback` works. Add `--dry-run` as the middle ground that renders server-side with validation. See [what Helm is](../container-orchestration-advanced/what-is-helm.md).
- For chart layout, list the real files: `Chart.yaml`, `values.yaml`, `templates/`, `templates/_helpers.tpl`, `templates/NOTES.txt`, `charts/` for subchart dependencies, `Chart.lock`, and `.helmignore`. Then explain `_helpers.tpl` specifically — named template definitions such as `fullname` and the standard label block, defined once with `define` and reused with `include`, and it renders nothing itself because the leading underscore excludes it from being treated as a manifest.
- CSI and CNI are asked back to back, so contrast them: both are pluggable interfaces that moved vendor code out of the Kubernetes tree, CSI for storage — provisioning, attaching, mounting volumes, snapshots — and CNI for Pod networking, assigning IPs and wiring the dataplane. Say why the interfaces exist: so a storage or network vendor can ship a driver without a Kubernetes release. See [container runtime interface](../container-orchestration-advanced/what-is-container-runtime-interface-cri.md).
- The Key Vault plus `.pfx` question is the most product-specific in the round, so be concrete: store the certificate as a Key Vault certificate, give Application Gateway a user-assigned managed identity with get permissions on secrets, and reference the certificate's _versionless_ secret identifier in the listener so a rotated certificate is picked up automatically. That versionless-URI detail is the whole point — with a pinned version, rotation silently does nothing. For AKS, either terminate TLS at Application Gateway with the ingress controller managing it, or use the Secrets Store CSI driver to mount the certificate into the ingress controller. See [what SSL/TLS is](../network-security/what-is-ssl-tls.md).
- A service principal is a non-human identity for an application, with a client ID and either a secret or a certificate, granted Azure RBAC roles on a scope. Say that a managed identity is the better answer wherever it is available, because there is no credential to store or rotate — offering that improvement is what senior candidates do. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- Secure service-to-service communication should reach mutual TLS with short-lived workload identities, plus authorisation at the API layer — OAuth 2.0 client credentials or JWT validation — and network policy restricting who can even reach the service. If a mesh is in play, say the mesh issues and rotates the certificates so the application does not have to. See [zero-trust security](../network-security/what-is-zero-trust-security.md) and [what Istio is](../container-orchestration-advanced/what-is-istio.md).
- For securing many microservices and websites at once, answer with a platform rather than per-service effort: a single ingress or gateway layer terminating TLS with automated certificates, a WAF in front, centralised authentication, default-deny network policies, admission control enforcing non-root and image provenance, image scanning in the pipeline, and secrets from a vault. The point is that security is applied once at the platform and inherited, not re-implemented per service. See [what a DevSecOps pipeline looks like end to end](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md) and [enforcing admission control with Kyverno or OPA Gatekeeper](../devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md).
- The launch-traffic question wants preparation, not reaction: load test to a known ceiling beforehand, pre-scale ahead of the launch rather than relying on reactive autoscaling, put a CDN in front of static and cacheable content, add caching and connection pooling at the data tier, protect with rate limiting, and have a graceful-degradation path — shed non-essential features rather than failing entirely. Say that autoscaling alone loses the first few minutes, which is exactly when a launch spike arrives. See [designing a system to degrade gracefully under overload](../scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md) and [auto-scaling](../scalability-and-high-availability/what-is-auto-scaling.md).
- Bringing a manual resource under management is `terraform import`, or better, an `import` block in configuration so the operation is planned and reviewable. Note that import populates state but does not write the HCL — you still author the resource block to match, and `terraform plan` showing no changes is how you prove you got it right. See [importing existing cloud infrastructure into Terraform](../infrastructure-as-code/how-do-you-import-existing-cloud-infrastructure-into-terraform.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
