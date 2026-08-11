---
title: "What DevOps interview questions does NatWest Group ask?"
id: 352
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - natwest-group
  - cicd
  - version-control
  - kubernetes
  - linux-administration
---

# What DevOps interview questions does NatWest Group ask?

## Questions

**Maven and the Java build chain**

- **Tell me about the Maven release process.**
- **Explain the Maven lifecycle.**
- **Tell me about the dependency management tag.**
- **What happens when you run `mvn install`?**
- **Where does your `pom.xml` live — in which directory?**

**Kubernetes and Git**

- **How did you manage Kubernetes Pods — it runs on Linux, correct?**
- **Which branching strategies are you using?**

## Example

```text
NatWest Group — DevOps Engineer, reported round
7 questions

  Maven / Java build chain    5   release process, lifecycle, dependencyManagement,
                                  mvn install behaviour, pom.xml location
  Kubernetes                  1   managing Pods (and the Linux premise)
  Git                         1   branching strategies

THE MOST UNUSUAL WEIGHTING IN THIS COLLECTION
  Five of seven questions are about Maven. No Terraform, no cloud provider,
  no Docker. A bank running large Java estates interviews for the build
  chain a release engineer actually touches — so revise Maven, not Kubernetes,
  before this one.
```

```text
MAVEN LIFECYCLE — the default phases, in order

  validate -> compile -> test -> package -> verify -> install -> deploy

  install  = puts the artefact in your LOCAL repository (~/.m2/repository)
  deploy   = puts it in the REMOTE repository (Nexus / Artifactory)

  Running a phase runs every phase before it. `mvn install` therefore
  compiles, tests, and packages first — which is why a failing unit test
  stops an install.
```

## Interview tips

- `mvn install` is the question most likely to be answered imprecisely, and the precise answer scores well. Because Maven's lifecycle is sequential, `install` runs every earlier phase — validate, compile, test, package, verify — and then copies the resulting artefact plus its POM into your **local** repository at `~/.m2/repository`, making it available to other projects on that machine. The distinction that matters is `install` (local) versus `deploy` (remote repository such as Nexus or Artifactory). Add that a failing test halts the install unless you skip tests, and that `-DskipTests` compiles them while `-Dmaven.test.skip=true` does not even compile them — that pair is a common follow-up.
- For the lifecycle, name the phases in order and then make one structural point: there are three lifecycles — `default`, `clean`, and `site` — and plugin goals bind to phases, which is why `mvn clean install` is two lifecycles invoked in sequence rather than one long chain.
- The `dependencyManagement` question has a specific answer that is easy to get half-right. `dependencyManagement` **declares** versions and scopes centrally without adding the dependency to the build; child modules then list the dependency without a version and inherit it. Contrast it with a plain `dependencies` block, which actually adds the dependency. Say why it exists: it keeps versions consistent across a multi-module project and lets you control transitive versions from one place. Mention nearest-definition-wins as Maven's conflict resolution rule, and BOM imports with `scope: import` as how you consume something like the Spring Boot dependency set.
- The Maven release process should be described as a release _engineer_ would: `mvn release:prepare` strips the `-SNAPSHOT` suffix, tags the source control revision, and bumps the version to the next snapshot; `mvn release:perform` checks out that tag and deploys the artefact to the remote repository. Then say the important properties — release versions are immutable and must never be republished, while snapshots are mutable and re-resolved, which is why production only ever runs a release version. If your team uses a CI-driven approach instead, say so and describe how the version is derived and where the artefact is published; interviewers accept either, but they want to hear that immutability is the point.
- `pom.xml` lives in the project root, with each module of a multi-module build having its own alongside a parent aggregator POM at the top level. Answer it plainly and then add the useful detail — the parent POM holds shared configuration and the `<modules>` list, and `mvn` resolves inheritance from it, which is where `dependencyManagement` usually sits. Linking the two questions like that shows the answers are connected knowledge rather than recalled facts.
- The Kubernetes question is phrased as a leading premise — "it is on Linux, right?" — and the correct move is to confirm it and add substance rather than just agreeing. Yes: containers share the host kernel, so Linux containers need Linux nodes, and while Windows node pools exist, they run Windows containers only. Then answer the real question about managing Pods: you do not manage Pods directly, you declare a Deployment or StatefulSet and let controllers reconcile the Pods, and you interact through `kubectl get`, `describe`, `logs`, and `rollout`. Saying "I manage workload controllers, not Pods" is the answer a platform engineer gives. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md) and [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- With only seven questions, each one carries real weight, so do not give one-line answers. Extend each Maven answer into the operational consequence — reproducible builds, why a proxy repository exists so builds do not depend on Maven Central being reachable, and why the local `.m2` cache causes "works on my machine" failures in CI. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md).
- On branching strategy, pick the model you have actually run, name it, and cover the two things a bank cares about: how a hotfix reaches production without dragging unreleased work with it, and how branches map to environments and release approvals. See [Git branching strategy](../version-control/what-is-git-branching-strategy.md) and [trunk-based development](../version-control/what-is-trunk-based-development.md).
- Expect the unasked follow-up in a Java-heavy shop: where dependencies come from and how you handle a vulnerable transitive one. Have `mvn dependency:tree`, a proxy repository, and dependency scanning ready. See [SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
