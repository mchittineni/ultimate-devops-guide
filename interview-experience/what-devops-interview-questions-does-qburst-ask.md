---
title: "What DevOps interview questions does Qburst ask?"
id: 372
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - qburst
  - gcp-engineering
  - kubernetes
  - infrastructure-as-code
  - docker
  - network-security
  - cloud-cost-optimization
---

# What DevOps interview questions does Qburst ask?

## Questions

**Kubernetes and GKE**

- **What are the different Service types?**
- **What is NodePort, and in which cases would you use it?**
- **What are LoadBalancer Services used for?**
- **What is the `kubectl` command to list Pods on a specific node?**
- **How do you restrict public access to load balancers, either standalone or in GKE?**
- **How do you migrate VMs from one GKE node pool to another?**

**GCP networking and services**

- **What is the major difference between an AWS VPC and a GCP VPC?**
- **If a VM is deployed in a private subnet, how do you run patch updates such as `apt update`?**
- **What is IAP in GCP?**
- **What is VPC connector — Serverless VPC Access?**
- **How do you reduce Cloud Storage bucket costs in GCP?**

**Terraform**

- **How do you ensure a Terraform-provisioned resource is not deleted when its configuration block is removed from the code?**
- **How do you handle different environments in Terraform?**
- **Is it possible to move the state file to a remote backend after it has already been created locally?**

**Docker**

- **What is the difference between `ADD` and `COPY` in a Dockerfile?**
- **How do you reduce the Docker build size?**
- **How do you pass a value into a Docker image at build time?**

## Example

```text
Qburst — DevOps Engineer (3-5 YOE), reported round
17 questions

  GCP networking / services   5   AWS vs GCP VPC, patching a private VM,
                                  IAP, Serverless VPC Access, bucket costs
  Kubernetes and GKE          6   Service types, NodePort cases, LoadBalancer,
                                  Pods on a node, restrict public LBs,
                                  node pool migration
  Terraform                   3   keep a resource when its config is removed,
                                  environments, local -> remote state
  Docker                      3   ADD vs COPY, reduce build size, build-time
                                  value

THE ONLY GCP-WEIGHTED ROUND IN THIS COLLECTION
  Five questions are GCP-specific — IAP, Serverless VPC Access, node pool
  migration, and the AWS-versus-GCP VPC model. If your background is AWS,
  these four terms are the gap to close before this interview.
```

## Interview tips

- The AWS-versus-GCP VPC question has one headline answer: **a GCP VPC is global, and its subnets are regional**, whereas an AWS VPC is regional with subnets scoped to a single availability zone. That single difference cascades into everything else worth mentioning — a GCP subnet spans all zones in its region, so you do not create one subnet per zone; routes and firewall rules are VPC-wide rather than per-subnet; GCP firewall rules are stateful with priorities and both allow and deny, so they combine the roles of security groups and NACLs; and GCP has no NAT gateway per se but Cloud NAT as a regional managed service. Leading with global-versus-regional is what shows you actually understand the model rather than having memorised service names.
- IAP — Identity-Aware Proxy — is the GCP answer to "how do I reach something private without a VPN or bastion". It authenticates and authorises users at the application layer before traffic reaches the resource, so you can expose a web application to specific identities with no public exposure of the backend, and IAP TCP forwarding gives you SSH or RDP to a VM with no external IP and no bastion host. Say it is the closest GCP equivalent to Session Manager plus a zero-trust access proxy, and that it enforces IAM rather than network position. See [zero-trust security](../network-security/what-is-zero-trust-security.md).
- Serverless VPC Access — the "VPC connector" — is what lets serverless products such as Cloud Run, Cloud Functions, and App Engine reach private resources inside your VPC by internal IP, because those services run outside your network by default. Say the direction matters: the connector handles egress _from_ serverless _into_ the VPC, and Private Service Connect or an internal load balancer is what you use for the reverse.
- The private-VM patching question is the same shape on every cloud, so give the options and the trade-off: Cloud NAT for outbound-only internet access so `apt update` can reach the distribution mirrors; or a Private Google Access route plus an internal package mirror or artefact repository so nothing leaves the network at all; or OS Config's patch management, which orchestrates patching without you opening a shell. Say that "no inbound" is not the same as "no outbound", and that the mirror approach is what regulated environments choose. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- The Terraform "do not delete when the config is removed" question is a favourite because people reach for `prevent_destroy`, which is _wrong_ here. `lifecycle { prevent_destroy = true }` makes the apply **fail** rather than preserving the resource, so it is a guard, not a release mechanism. The correct answer is `terraform state rm <address>`, which removes the resource from state so Terraform forgets it and stops managing it — the infrastructure keeps running untouched. Say both: `state rm` to release ownership deliberately, `prevent_destroy` to stop an accidental destroy, and `removed` blocks in current Terraform as the reviewable, declarative way to do the former. Distinguishing those three is the whole question. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- Yes, you can move local state to a remote backend after the fact, and the sequence is worth giving precisely: add the `backend` block, run `terraform init -migrate-state`, confirm at the prompt that you want to copy the existing state, then verify with `terraform plan` showing no changes and delete the local file. Say that the empty plan is how you prove the migration worked, and that you should never commit `terraform.tfstate` in the meantime because it can contain secrets in plain text.
- Restricting public access to load balancers has a GKE-specific answer worth naming: use an _internal_ load balancer — a Service annotated for internal load balancing, or an internal Ingress or Gateway — so it gets an RFC 1918 address reachable only within the VPC. For a load balancer that must be public, put Cloud Armor in front with IP allowlists and WAF rules, or front it with IAP so only authenticated identities get through. Say that setting a Service to `LoadBalancer` in GKE creates an _external_ one by default, which is exactly the mistake the question is probing.
- Node pool migration in GKE is a cordon-and-drain exercise, and the ordered answer is: create the new node pool with the desired machine type or version, `kubectl cordon` the old nodes so nothing new schedules there, then `kubectl drain` them one at a time respecting PodDisruptionBudgets and using `--ignore-daemonsets`, let the workloads reschedule onto the new pool, verify, then delete the old pool. Mention that Pods with node-local storage or a `ReadWriteOnce` volume need attention, and that GKE's surge upgrades do this for you within a pool. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- The command for Pods on a specific node is `kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName=<node>`. Knowing `--field-selector` rather than piping through `grep` is the point of the question; add `kubectl describe node <node>` to see the same information alongside allocated resources.
- Service types should each come with the use case they asked for: ClusterIP as the internal default; NodePort opening the same port in the 30000-32767 range on every node, useful for development, on-premises clusters with an external load balancer, or as the substrate LoadBalancer builds on — and a poor production front door because you must track node addresses; LoadBalancer to have the cloud provision a real load balancer per Service; ExternalName to alias an external DNS name; and headless for direct per-Pod addressing. Say that one Ingress behind a single load balancer is what you use rather than a LoadBalancer per service, for cost and manageability. See [what a Service is in Kubernetes](../kubernetes/what-is-a-service-in-kubernetes.md) and [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- The build-time value question is `ARG` plus `--build-arg`, and the important half is the warning: `ARG` values are visible in the image history, so they must never carry a secret. For secrets at build time use BuildKit's `--mount=type=secret`, which exposes the value only during that step and leaves nothing in a layer. Distinguish `ARG` (build time) from `ENV` (build and run time) — that pair is the natural follow-up. See [what a Dockerfile is](../docker/what-is-dockerfile.md).
- On reducing build size, prioritise rather than list: a multi-stage build so compilers and dev dependencies never ship, a minimal base such as Alpine or distroless, cleaning package caches within the same `RUN` layer, a `.dockerignore` so the build context stays small, and copying only the built artefact. Say you would run `docker history` to find the fat layer instead of guessing, and pair it with `COPY` over `ADD` as the default. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- GCP bucket cost reduction maps onto the same ideas as S3 but with GCP names: lifecycle rules transitioning to Nearline, Coldline, and Archive; Autoclass when the access pattern is unpredictable; deleting noncurrent object versions; aborting incomplete multipart uploads; choosing regional over multi-region storage when you do not need geo-redundancy; and watching egress, which is frequently the larger line item. See [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[What is the difference between SRE, DevOps, and Platform Engineering?]] (`#232`): [What is the difference between SRE, DevOps, and Platform Engineering?](../site-reliability-engineering/what-is-the-difference-between-sre-devops-and-platform-engineering.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
