---
title: "What DevOps interview questions does Intact Green Services ask?"
id: 342
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - intact-green-services
  - kubernetes
  - cicd
  - infrastructure-as-code
  - docker
  - aws-engineering
  - core-devops-concepts
---

# What DevOps interview questions does Intact Green Services ask?

## Questions

**Kubernetes**

- **What is desired state and what is the undesired (actual) state?**
- **How do you deploy an application in Kubernetes?**
- **What are the Service types in Kubernetes, and what is each one's use case?**

**Jenkins**

- **Have you hit a memory problem in a Jenkins pipeline? How would you troubleshoot it?**
- **What are the different types of Jenkins pipeline?**
- **What are the advantages of a multibranch pipeline?**
- **Can a Pod be used as a Jenkins agent, and what are the drawbacks of doing so?**
- **Which tools have you used for CI/CD pipelines?**

**Networking**

- **There are two VPCs, A and B. Give me the options for making A and B communicate both ways — and also the option where only A needs to reach B.**

**Terraform**

- **Two instances were created with Terraform. The state file exists both locally and in a remote S3 backend. If a user deletes one instance, what happens, and how do you handle it?**

**Docker**

- **A Docker image is causing problems because of its size. What is your action plan to reduce it?**
- **You cannot push an image to Docker Hub because of an access problem. Where else can you push it?**

## Example

```text
Intact Green Services — DevOps Engineer (5 YOE), reported round
12 questions

  Jenkins                     5   pipeline memory issue, pipeline types,
                                  multibranch advantages, Pod as agent
                                  (+ drawbacks), CI/CD tools used
  Kubernetes                  3   desired vs actual state, deploying an app,
                                  Service types with use cases
  Docker                      2   reduce image size, alternatives to Docker Hub
  Terraform                   1   local AND remote state, one instance deleted
  Networking                  1   VPC A<->B, and A->B only

THE TWO QUESTIONS WITH A HIDDEN CATCH
  "State file is local AND in S3" is not a normal setup — the interviewer
  planted the contradiction. "Only A has to communicate to B" is asking for
  a one-directional answer, which peering cannot give you.
```

## Interview tips

- The Terraform question contains a deliberate contradiction, and spotting it is the answer. Terraform uses exactly one backend at a time: if the `backend "s3"` block is configured and initialised, S3 is authoritative and the local file is a stale leftover from before migration. So say that first, then answer what actually happens when someone deletes an instance out of band — the next `plan` detects the resource is gone and proposes recreating it, because state still claims it exists. Handling it means either applying to restore it or, if the deletion was intended, removing it from the configuration and letting `plan` reconcile. Close with prevention: delete the stale local file, enforce apply-only-from-CI, deny console delete permissions, and run scheduled `plan -refresh-only` for drift detection. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The VPC question is asked in two halves on purpose. For bidirectional connectivity: VPC peering with routes and security-group rules on both sides, or Transit Gateway if you expect more VPCs and want transitive routing, or a VPN between them. For "only A reaches B", say plainly that peering is inherently bidirectional at the routing layer — you cannot make the route one-way — so you enforce direction with security groups and NACLs, or better, use PrivateLink, which is genuinely unidirectional by design: B exposes a service behind an NLB and A consumes it through an interface endpoint, with no route between the VPCs at all. Naming PrivateLink as the correct one-way answer is what wins this question. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- "Can a Pod be a Jenkins agent, and what are the drawbacks?" — yes, via the Kubernetes plugin, which creates an ephemeral Pod per build and destroys it afterwards, giving clean isolated workspaces and capacity that scales with demand. The drawbacks are the real question, so name them: Pod startup and image pull add latency to every build, nothing is cached between builds unless you mount a persistent volume or use a remote cache, Docker-in-Docker needs privileged mode or a rootless alternative such as Kaniko or Buildkit, resource requests must be right-sized or builds get OOMKilled, and losing a node mid-build loses the build. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- The Jenkins memory question has a specific first step that most candidates skip: distinguish the _controller_ running out of heap from the _build_ running out of memory. Controller symptoms are slowness and `OutOfMemoryError` in the controller log, usually caused by too much build history, huge console logs, or heavy Groovy in a pipeline — fix by raising `-Xmx`, trimming `buildDiscarder`, and moving logic out of the controller. Build-side symptoms are the JVM or a container being killed — fix by raising the agent's memory, setting `MAVEN_OPTS` or `JAVA_TOOL_OPTIONS`, and never building on the controller. Saying "first I would establish which side is out of memory" is the answer.
- Desired versus actual state is the core of Kubernetes' control model, so answer it with the loop rather than a definition: you declare desired state in an object, controllers continuously observe actual state, compute the difference, and act to close the gap — which is why deleting a Pod owned by a Deployment gets you a new Pod. Say "reconciliation loop" and give that example.
- On Service types, pair every type with the use case they asked for: ClusterIP for internal-only traffic and the default; NodePort for exposing a fixed port on every node, mostly for development or as a target for an external load balancer; LoadBalancer to have the cloud provision a real load balancer per Service; ExternalName to alias an external DNS name; and headless (`clusterIP: None`) for direct Pod addressing, which is what StatefulSets use. See [what a Service is in Kubernetes](../kubernetes/what-is-a-service-in-kubernetes.md) and [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- Image size reduction should be a prioritised plan, not a list: multi-stage builds so the toolchain never ships, a minimal base such as Alpine or distroless, combining `RUN` layers and cleaning package caches in the same layer, a `.dockerignore` so build context and secrets stay out, copying only the built artefact, and pinning to a slim variant. Say which gives the biggest win — multi-stage plus a minimal base usually accounts for most of it — and mention that you would measure with `docker history` to find the fat layer. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- Registry alternatives should show you know a registry is a standard API, not a product: ECR, Azure Container Registry, Google Artifact Registry, GitHub Container Registry, GitLab's built-in registry, Quay, Harbor or a self-hosted OCI registry, or Nexus and Artifactory if the organisation already runs one. Add that in an enterprise you would prefer a private registry with image scanning and immutable tags regardless of the access problem. See [signing and verifying container images](../devsecops/how-do-you-sign-and-verify-container-images.md).
- Multibranch advantages: a job is created automatically for every branch and pull request from the `Jenkinsfile` in that branch, jobs disappear when branches are deleted, each branch gets isolated builds so feature work is validated before merge, and pipeline configuration is versioned with the code it builds. That last point — configuration travelling with the branch — is the strongest single advantage.
- Pipeline types: declarative and scripted as the two syntaxes, plus multibranch and organisation-folder as job types, and freestyle as the legacy non-pipeline option. Say you default to declarative.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
