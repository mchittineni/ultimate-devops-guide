---
title: "What DevOps interview questions does Hexaware ask?"
id: 337
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - hexaware
  - azure-engineering
  - cicd
  - kubernetes
  - infrastructure-as-code
  - container-orchestration-advanced
  - version-control
  - devsecops
---

# What DevOps interview questions does Hexaware ask?

## Questions

**Azure Pipelines**

- **Write a YAML pipeline for CI/CD — the overall structure.**
- **How do you configure an approval gate in a CD pipeline?**
- **What is a variable group in Azure DevOps?**
- **How do you promote code from one environment to the next?**
- **What branching strategies do you use?**

**Kubernetes and Helm**

- **What is a `deployment.yml` and what does it define?**
- **What is a `service.yml` and what does it define?**
- **What is a ReplicaSet?**
- **What does a Helm chart produce as output?**
- **Which files exist inside a Helm chart?**

**Terraform**

- **What is the command for auto-approval in Terraform?**
- **Write sample Terraform code — the overall skeleton.**

**Tooling and automation**

- **What is SonarQube and what is it used for?**
- **What is Storage Explorer?**
- **Have you written automation scripts as part of your daily work?**

## Example

```text
Hexaware — DevOps Engineer (4-5 YOE), reported round
15 questions — Azure DevOps flavoured

  Azure Pipelines             5   write YAML pipeline, CD approvals,
                                  variable groups, environment promotion,
                                  branching strategy
  Kubernetes and Helm         5   deployment.yml, service.yml, ReplicaSet,
                                  Helm output, chart files
  Terraform                   2   auto-approve flag, skeleton code
  Tooling                     3   SonarQube, Storage Explorer, own automation

TWO "WRITE IT" QUESTIONS
  A YAML pipeline and a Terraform skeleton, both asked for structure rather
  than detail. Practise typing both from memory — the marks are for correct
  top-level keys, not clever content.
```

```yaml
# Azure Pipelines skeleton — the structure they are asking for.
trigger:
  branches:
    include: [main, release/*]

variables:
  - group: prod-secrets # <- the variable group question
  - name: imageTag
    value: $(Build.BuildId)

stages:
  - stage: Build
    jobs:
      - job: build
        pool: { vmImage: ubuntu-latest }
        steps:
          - script: make build
          - task: SonarQubePublish@5

  - stage: DeployProd
    dependsOn: Build
    jobs:
      - deployment: prod # deployment job + environment
        environment: production # <- approvals attach HERE, not in YAML
        strategy:
          runOnce:
            deploy:
              steps:
                - script: helm upgrade --install app ./chart
```

## Interview tips

- The approval question has a specific answer in Azure DevOps that catches people out: approvals are **not** defined in the YAML. You attach an approval check to an _environment_ (Pipelines → Environments → Approvals and checks), and the YAML only references that environment from a `deployment` job. Say that clearly, then mention the other check types — branch control, business hours, invoke REST API, and required template — because "approvals and checks" is the phrase they are listening for. In classic release pipelines it was pre- and post-deployment approvals on the stage.
- A variable group is a named, reusable set of variables stored in the Library, shareable across pipelines and optionally linked to Azure Key Vault so secrets are pulled at runtime rather than stored in the group. Say the Key Vault link — that is the part that shows production use, and it also answers how you keep secrets out of YAML.
- `terraform apply -auto-approve` is the command, and the answer worth giving is one sentence longer: you use it in CI where a human has already reviewed the plan, and the safer pattern is `terraform plan -out=tfplan` followed by `terraform apply tfplan`, because applying a saved plan guarantees you are applying exactly what was reviewed. `-auto-approve` also applies to `destroy`, which is where it becomes dangerous. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- "What is the output of a Helm chart" is asking about rendering: a chart plus its values renders to plain Kubernetes manifests, which Helm submits to the API server and records as a versioned release. Say that `helm template` shows you that output without touching the cluster, and that the release history is what makes `helm rollback` possible. See [what Helm is](../container-orchestration-advanced/what-is-helm.md).
- For chart contents, list the real files: `Chart.yaml`, `values.yaml`, `templates/` with `_helpers.tpl` and `NOTES.txt`, `charts/` for dependencies, `Chart.lock`, and `.helmignore`.
- On `deployment.yml` and `service.yml`, do not just define them — connect them. The Deployment declares the desired replica count, Pod template, image, and update strategy, and owns a ReplicaSet that owns the Pods; the Service gives that set of Pods a stable virtual IP and DNS name and selects them by label. The label selector matching is the link the interviewer wants you to draw. See [what a Service is in Kubernetes](../kubernetes/what-is-a-service-in-kubernetes.md) and [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- ReplicaSet should be answered with why you rarely touch one directly: it maintains a stable set of replicas, but the Deployment manages ReplicaSets on your behalf to give you rolling updates and rollback, so creating one by hand is unusual.
- Environment promotion is a chance to state a principle rather than a mechanism: build the artefact once and promote _that same artefact_ through dev, QA, and production, changing only configuration. Say that rebuilding per environment means you never tested what you shipped. Then name the mechanism you use — stage dependencies with approvals, or a GitOps repository per environment. See [continuous delivery versus continuous deployment](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md).
- Storage Explorer is a small question with an easy trap — it is a Microsoft desktop and web tool for browsing and managing Azure Storage accounts (blobs, files, queues, tables), useful for inspecting or transferring data. It is a client tool, not a service; say that so you do not sound like you are guessing.
- SonarQube: static analysis for bugs, vulnerabilities, code smells, coverage, and duplication, enforced as a quality gate that fails the build. Add that gating on _new_ code rather than the whole legacy baseline is what makes it adoptable. See [what shift-left security means](../devsecops/what-does-shift-left-security-mean.md).
- The automation-scripts question is an invitation, not a yes-or-no. Have one concrete example ready with the outcome — a script that cleaned up untagged resources, rotated logs, or generated a report — including roughly how much time it saved. See [turning ad-hoc scripts into maintainable automation](../scripting-and-automation/how-do-you-turn-a-pile-of-ad-hoc-scripts-into-maintainable-automation.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
