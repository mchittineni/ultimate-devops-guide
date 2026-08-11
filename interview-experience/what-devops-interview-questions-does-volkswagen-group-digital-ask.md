---
title: "What DevOps interview questions does Volkswagen Group Digital ask?"
id: 390
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - volkswagen-group-digital
  - cicd
  - azure-engineering
  - devsecops
  - kubernetes
  - scripting-and-automation
  - api-gateway-and-service-mesh
---

# What DevOps interview questions does Volkswagen Group Digital ask?

## Questions

The submitter noted the role was scoped at roughly 70% DevOps and 30% development, which explains the REST API question at the end.

**Onboarding and automation**

- **How do you onboard a new project from code through to release management, across multiple environments such as dev, QA, and production?**
- **How do you automate all the steps in CI and CD when many tools are involved?**
- **How do you write CI/CD pipelines?**
- **Explain a CI/CD process you have worked on, with all the steps.**

**Security and reliability**

- **How do you run security checks on a Docker image?**
- **What production issues have you faced in Kubernetes?**

**Scripting and Azure**

- **What was the most recent script you wrote?**
- **Which Azure services do you use?**
- **Which Azure DevOps services would you like to learn beyond what you already use?**

**Development**

- **What is a REST API?**

## Example

```text
Volkswagen Group Digital — DevOps Engineer, reported round
10 questions — role scoped 70% DevOps / 30% development

  Onboarding and automation   4   onboard a project end to end, automate
                                  across many tools, how you write pipelines,
                                  walk a real CI/CD process
  Security and reliability    2   Docker image security checks, real K8s
                                  production issues
  Scripting and Azure         3   your most recent script, Azure services
                                  used, what you want to learn next
  Development                 1   what a REST API is

A SMALL ROUND WHERE FOUR QUESTIONS ARE THE SAME QUESTION
  Onboarding, automating across tools, writing pipelines, and walking a real
  process are four angles on one story. Prepare that story once, in enough
  depth to answer all four differently.
```

## Interview tips

- The four delivery questions overlap heavily, so build one end-to-end narrative and enter it from four different doors rather than repeating yourself. Onboarding is about the _sequence_ of setting a project up: repository created from a template with branch protection and required checks, pipeline definition committed alongside the code, environments and their approvals defined, secrets provisioned in a vault with the pipeline given a federated identity rather than a stored key, infrastructure provisioned as code, observability and alerting wired in before the first release, and a runbook plus on-call ownership agreed. Say that the last two are the ones teams skip and then regret.
- The "many tools" question is really asking how you avoid a brittle chain of integrations. Give the principles: one orchestrator owns the flow and everything else is invoked from it, not from each other; each tool is called through a versioned reusable template or shared library so fifty projects do not each hand-roll it; the artefact is the contract between stages — built once, immutable, promoted rather than rebuilt; state lives in Git so the pipeline is reproducible; and secrets come from one store via short-lived identity. Then name the anti-pattern explicitly: tools triggering each other with webhooks in a chain nobody can draw, which is how you get a pipeline only one person understands. See [consolidating a sprawling DevOps toolchain](../devops-tools-and-automation/how-do-you-consolidate-a-sprawling-devops-toolchain.md).
- For "explain a CI/CD process with all the steps", give a real one stage by stage and name the gate at each: commit triggers build, unit tests, static analysis with a quality gate on new code, dependency and container scanning, image built once and tagged with the Git SHA, pushed to a registry, deployed automatically to dev, integration and smoke tests, promotion to QA behind an approval, then production behind a change gate with a canary or blue-green cutover and automated rollback on regression. Say the two things that make it credible: the same artefact is promoted upward without rebuilding, and every gate can fail the pipeline. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md) and [continuous delivery versus continuous deployment](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md).
- The multi-environment question deserves the promotion principle stated plainly: build once, promote the identical artefact through dev, QA, and production, changing only configuration. Rebuilding per environment means you never tested what you shipped. Then the mechanism you actually use — stage dependencies with environment approvals, or a GitOps repository per environment where promotion is a pull request changing an image tag — and say how configuration differs without the artefact differing: environment-scoped variable groups or value files, never branching the code.
- Docker image security checks should be a pipeline sequence rather than a tool name, because that is what "how do you run security checks" is asking. In CI: scan the image with Trivy or Grype and fail on severity thresholds you have agreed, scan dependencies separately since most findings come from the base image, lint the Dockerfile with Hadolint, generate an SBOM so you can answer "are we affected" later without rebuilding, and sign the image with Cosign. At the registry: scan on push and enable tag immutability. At admission: enforce that only signed images from approved registries can run, using Kyverno or OPA Gatekeeper. Then the runtime hardening in the Dockerfile itself — minimal or distroless base pinned by digest, multi-stage build, non-root user, read-only root filesystem, no secrets in `ARG` or `ENV`. Say that you gate on _reachable_ severity rather than raw CVE count, otherwise the gate gets disabled within a month. See [SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md), [signing and verifying container images](../devsecops/how-do-you-sign-and-verify-container-images.md), and [what a DevSecOps pipeline looks like end to end](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md).
- "What production issues have you faced in Kubernetes?" is the highest-value question in the round because it is unfakeable. Come with two or three specific incidents, each told as symptom, wrong first hypothesis, actual cause, fix, and the preventive change. Good candidates from real estates: a Pod `OOMKilled` because the JVM did not respect its cgroup memory limit until `MaxRAMPercentage` was set; an aggressive liveness probe restarting a healthy-but-slow container during a dependency slowdown, turning a partial degradation into an outage; a node drain hanging indefinitely on a PodDisruptionBudget during an upgrade; a Service with empty `Endpoints` after a label-selector change, so traffic went nowhere while every Pod looked healthy; or subnet IP exhaustion on EKS because the VPC CNI assigns an address per Pod. Naming the preventive change each time is what turns a war story into evidence of engineering. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md) and [how probes differ](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md).
- "What was the most recent script you wrote?" is a calibration question and a one-line answer wastes it. Describe the problem it solved, the decisions in it — argument validation, `set -euo pipefail` or non-zero exit codes, idempotency so a re-run is safe, logging so a failure is diagnosable — how it is scheduled or invoked, and what it replaced. Then add the maturity point: say whether it should have been a script at all, or whether the real fix was a `systemd` timer, a Kubernetes CronJob, or a change upstream that removed the need. See [turning a pile of ad-hoc scripts into maintainable automation](../scripting-and-automation/how-do-you-turn-a-pile-of-ad-hoc-scripts-into-maintainable-automation.md) and [writing a production-grade Bash script](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md).
- The "what would you like to learn" question is not filler — it tests self-awareness and whether you keep current. Name something specific and adjacent with a reason, not a shopping list: Azure Deployment Environments for self-service provisioning, workload identity federation to eliminate stored service-principal secrets, or Gateway API on AKS as Ingress is superseded. Saying _why_ it matters to the work is the whole answer.
- For the Azure services question, group rather than list, and be honest about depth: compute (AKS, App Service, Functions), networking (Application Gateway, Front Door, Private Endpoints, Firewall), identity (Entra ID, managed identities), data (SQL Database, Storage accounts, Cosmos DB), platform (Key Vault, Container Registry, Monitor with Log Analytics), and delivery (Azure DevOps or GitHub Actions, Bicep or Terraform). Then say which two or three you have genuinely operated in production versus which you have only used — the honesty is worth more than the breadth, because the follow-up will test it.
- The REST API question exists because the role is 30% development, so answer it as an engineer rather than reciting an acronym: an architectural style over HTTP where resources are identified by URIs and manipulated with the standard methods, communication is stateless so each request carries everything needed, and responses are cacheable. Then give the substance that shows you have built and operated one: correct method semantics and idempotency — `GET`, `PUT`, and `DELETE` idempotent, `POST` not, which is why a retried `POST` needs an idempotency key; meaningful status codes (`200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `429`, `500`, `503`); versioning so you can evolve without breaking clients; pagination and rate limiting; and authentication with OAuth 2.0 bearer tokens or mTLS. Contrast briefly with gRPC and GraphQL to show you know when REST is not the right choice. See [what a web application firewall is](../network-security/what-is-a-web-application-firewall-waf.md) for the operational side of exposing one.
- With ten questions and four of them overlapping, the risk in this round is sounding repetitive. Decide in advance which detail belongs to which question — sequence and governance for onboarding, integration architecture for the many-tools question, syntax and templating for how you write pipelines, and a concrete narrative for the walkthrough — so each answer adds something new.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
