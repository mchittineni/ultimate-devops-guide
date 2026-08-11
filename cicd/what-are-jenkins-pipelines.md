---
title: "What are Jenkins Pipelines?"
id: 18
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
---

# What are Jenkins Pipelines?

**Short answer:** A Jenkins Pipeline is a build workflow defined as code in a `Jenkinsfile`, expressed as stages and steps, versioned with the application, and able to survive controller restarts.

## Detail

**Declarative vs scripted.** Declarative pipelines use a fixed `pipeline { agent … stages { … } }` structure with validation and clear error messages - the default recommendation. Scripted pipelines are raw Groovy, offering full programmatic control for unusual cases.

**Key constructs:**

- `agent` - where the pipeline or a stage runs (any node, a label, a Docker image, a Kubernetes pod template).
- `stages` / `steps` - the logical phases and the commands inside them.
- `environment` - variables at pipeline or stage scope, including credential bindings.
- `when` - conditional stage execution (branch, tag, changeset, expression).
- `parallel` - run stages concurrently to cut wall-clock time.
- `input` - pause for human approval, typically before production.
- `post` - `always` / `success` / `failure` / `unstable` blocks for reporting and cleanup.
- `options` - timeouts, retry, build retention, concurrency control.

**Durability:** pipeline state is checkpointed, so a controller restart mid-build resumes rather than losing the run.

**Shared libraries** live in their own repository under `vars/` and `src/`, letting you call `standardBuild(language: 'java')` from every team's Jenkinsfile and change the implementation centrally.

## Example

```groovy
pipeline {
  agent none
  stages {
    stage('Verify') {
      parallel {
        stage('Unit')  { agent { label 'linux' } steps { sh 'make unit' } }
        stage('Lint')  { agent { label 'linux' } steps { sh 'make lint' } }
        stage('SAST')  { agent { label 'linux' } steps { sh 'make sast' } }
      }
    }
    stage('Approve') {
      when { branch 'main' }
      steps { timeout(time: 1, unit: 'HOURS') { input message: 'Deploy to production?' } }
    }
    stage('Deploy') { agent { label 'deploy' } steps { sh './deploy.sh' } }
  }
  post { failure { emailext to: 'team@example.com', subject: "Failed: ${currentBuild.fullDisplayName}" } }
}
```

## Interview tips

- Recommend declarative, and be able to say precisely when you would drop into `script { }` blocks.
- `parallel` plus per-stage agents is the standard answer to "how do you speed up a Jenkins build?"
- Shared libraries are the answer to pipeline sprawl across many repositories.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
