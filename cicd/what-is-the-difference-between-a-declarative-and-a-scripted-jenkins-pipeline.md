---
title: "What is the difference between a declarative and a scripted Jenkins pipeline?"
id: 454
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
---

# What is the difference between a declarative and a scripted Jenkins pipeline?

**Short answer:** Both are Groovy, both live in a `Jenkinsfile`, and both run on the same Pipeline engine - the difference is structure. A **declarative** pipeline opens with `pipeline { }` and imposes a fixed skeleton (`agent`, `stages`, `stage`, `steps`, `post`, `environment`, `options`), which Jenkins can validate before execution, render properly in Blue Ocean and the stage view, and give you built-in `post` conditions, `when` guards, `parallel`, `matrix`, and `options` such as timeouts and retries. A **scripted** pipeline opens with `node { }` and is essentially a Groovy program: you get full imperative control - loops, closures, try/catch, dynamic stage generation - but no schema validation, weaker visualisation, and much more scope to write something unmaintainable. The practical rule teams settle on: **write declarative by default**, and drop into a `script { }` block for the small imperative parts. Reach for fully scripted only when you genuinely need to generate the pipeline structure at runtime.

## Detail

### Side by side

|                                  | Declarative                                                      | Scripted                                         |
| -------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------ |
| Entry point                      | `pipeline { agent … stages { … } }`                              | `node('label') { … }`                            |
| Validated before running         | Yes - syntax errors are caught up front                          | No - it fails when it reaches the bad line       |
| Built-in `post` blocks           | `always`, `success`, `failure`, `unstable`, `changed`, `aborted` | You write `try/catch/finally`                    |
| Conditional stages               | `when { branch 'main' }`                                         | `if (env.BRANCH_NAME == 'main')`                 |
| Parallelism                      | `parallel` block, plus `matrix` for axes                         | `parallel([a: {…}, b: {…}])`                     |
| Timeouts / retries / concurrency | `options { timeout(...) disableConcurrentBuilds() }`             | Wrap steps in `timeout {}` / `retry {}` yourself |
| Dynamic stage names/count        | Awkward (needs `script`)                                         | Natural                                          |
| Visualisation                    | Full stage view / Blue Ocean                                     | Degraded                                         |
| Learning curve                   | Low - looks like configuration                                   | Needs Groovy                                     |

The behavioural difference candidates are asked about most: **where does a syntax error surface?** In a declarative pipeline the whole `Jenkinsfile` is parsed and validated first, so a typo in stage five fails the build immediately, before stage one runs. In a scripted pipeline execution is sequential Groovy, so stages one to four run, do real work, and _then_ it dies at stage five - which is why a broken deploy stage can leave you with a pushed image and no deployment.

### The declarative blocks worth knowing cold

- **`agent`** - where the work runs. `agent any`, `agent none` at top level with per-stage agents, `agent { label 'linux && docker' }`, `agent { docker { image 'maven:3.9' } }`, or `agent { kubernetes { yaml … } }` to run each build in a fresh Pod. Declaring `agent none` at the top and agents per stage is how you avoid holding an executor while waiting for an approval.
- **`environment`** - variables for the pipeline or a single stage, and the natural home for `credentials('id')`, which injects a secret and masks it in the log.
- **`options`** - `timeout(time: 30, unit: 'MINUTES')`, `retry(2)`, `buildDiscarder(logRotator(numToKeepStr: '30'))`, `disableConcurrentBuilds()`, `timestamps()`, `skipDefaultCheckout()`. A pipeline without a timeout is a pipeline that eventually wedges an executor forever.
- **`post`** - the reason declarative exists for most teams: `always` for cleanup and `junit`/`archiveArtifacts`, `failure` for notifications, `cleanWs()` at the end. In scripted you hand-roll this in `finally` and people forget.
- **`when`** - `branch`, `changeset`, `expression`, `tag`, `anyOf`/`allOf`, plus `beforeAgent true` so you do not spin up an agent just to decide to skip.
- **`parallel` and `matrix`** - `matrix` expands axes (OS × version) into parallel stages with `excludes`, which replaces a lot of hand-written scripted loops.
- **`input`** - a manual gate. Put it in a stage with `agent none` and a `timeout`, or an abandoned approval holds an agent indefinitely.

### Where scripted still earns its place

Generating stages from data - "one deploy stage per region in this list", "one test stage per service that changed in this commit" - is the honest use case, because declarative stage blocks are static. The idiomatic modern answer, though, is to keep the pipeline declarative and put the imperative logic in a **shared library**: a `vars/buildService.groovy` that returns a map of parallel branches, called from a `script` block. That keeps the `Jenkinsfile` readable, the logic tested and versioned in one place, and the same pipeline reusable across dozens of repositories.

### The constraints that catch people out in both forms

- **`Jenkinsfile` code runs on the controller** (except inside `sh`/`bat` steps on the agent). Heavy Groovy loops, big string manipulation, or parsing large files in the pipeline itself consume controller CPU and memory and slow down every other job.
- **CPS transformation.** Pipeline Groovy is continuation-passing-style so it can survive a controller restart, which is why many Groovy idioms misbehave - non-serializable objects across steps, `.each` with closures over `sh` calls, and iterators are all common sources of `java.io.NotSerializableException`. Use plain `for` loops, keep non-CPS logic in `@NonCPS` methods in a shared library, and do text processing in `sh` rather than Groovy.
- **Script approval**. Scripted pipelines and library code that touch internal APIs hit the Groovy sandbox and need administrator approval - a real friction point and, if approved carelessly, a security hole on the controller.
- **Both should be in the repository.** Pipeline-as-code with a multibranch job is the point; a pipeline pasted into the Jenkins UI has no review, no history, and no branch awareness.

## Example

```groovy
// Declarative: the default choice. Structure, guards, and cleanup are first-class.
pipeline {
  agent none                                     // no executor held at the top level
  options {
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '30'))
    timestamps()
  }
  environment {
    REGISTRY   = 'registry.example.com'
    IMAGE      = "${REGISTRY}/api:${env.GIT_COMMIT.take(12)}"
    SONAR_AUTH = credentials('sonar-token')      // injected and masked
  }
  stages {
    stage('Build & test') {
      agent { docker { image 'maven:3.9-eclipse-temurin-21'; args '-v $HOME/.m2:/root/.m2' } }
      steps { sh 'mvn -B verify' }
      post { always { junit 'target/surefire-reports/*.xml' } }
    }

    stage('Quality & security') {                 // independent checks, run together
      parallel {
        stage('SonarQube') {
          agent { label 'linux' }
          steps { sh 'mvn -B sonar:sonar' }
        }
        stage('Image scan') {
          agent { label 'linux' }
          steps { sh 'trivy image --severity HIGH,CRITICAL --exit-code 1 $IMAGE' }
        }
      }
    }

    stage('Deploy to prod') {
      when { branch 'main'; beforeAgent true }    // decide before allocating an agent
      steps {
        timeout(time: 1, unit: 'HOURS') {
          input message: 'Deploy to production?', ok: 'Ship it'
        }
        node('deployer') { sh "helm upgrade --install api ./chart --set image.tag=${IMAGE} --atomic" }
      }
    }
  }
  post {
    failure  { slackSend channel: '#deploys', message: "FAILED ${env.JOB_NAME} #${env.BUILD_NUMBER}" }
    always   { node('linux') { cleanWs() } }
  }
}
```

```groovy
// Scripted: worth it only when the structure itself is data-driven
node('linux') {
  try {
    stage('Checkout') { checkout scm }

    // the legitimate reason to be here: stages generated from a list
    def regions = readYaml(file: 'deploy/regions.yaml').regions
    def branches = [:]
    for (r in regions) {                          // plain for-loop: CPS-safe
      def region = r                              // capture, do not close over the iterator
      branches["deploy-${region}"] = {
        node('deployer') { sh "./deploy.sh ${region}" }
      }
    }
    stage('Deploy all regions') { parallel branches }
  } catch (e) {
    currentBuild.result = 'FAILURE'
    slackSend channel: '#deploys', message: "FAILED: ${e.message}"
    throw e
  } finally {
    cleanWs()                                     // you must remember this yourself
  }
}
```

```groovy
// The pattern most mature teams land on: declarative Jenkinsfile, logic in a library
@Library('platform-pipelines@v3') _
buildJavaService(
  serviceName: 'payments',
  registry:    'registry.example.com',
  deployTo:    ['dev', 'staging', 'prod'],
  sonarGate:   true
)
```

## Interview tips

- Answer structurally, not tribally: declarative imposes a validated schema with `post`, `when`, `options`, and `matrix`; scripted is Groovy with full control and no guard rails. Then give your recommendation - declarative by default, `script {}` for the awkward bits.
- The high-signal detail is **when errors surface**: declarative validates the whole file before running, scripted fails at the line it reaches. Give the consequence - a half-completed pipeline that pushed an image but never deployed.
- List the declarative blocks by name and purpose (`agent`, `environment`, `options`, `post`, `when`, `parallel`, `input`). Interviewers frequently ask "what are the `agent`, `post`, and `environment` blocks for?" directly.
- Volunteer `agent none` plus per-stage agents, and a `timeout` around any `input` - both stop approvals from pinning an executor for days.
- If asked whether more than two stages can run at once, say yes - `parallel` with as many branches as you like, or `matrix` for axis expansion - and note that agent availability, not the pipeline, is the real limit.
- Mention that `Jenkinsfile` Groovy executes on the **controller** and that CPS serialisation is why some Groovy idioms explode. That is the kind of detail only people who have debugged a `NotSerializableException` know.
- Land on shared libraries as the way to get scripted flexibility without unmaintainable `Jenkinsfile`s. See [what are Jenkins Pipelines](./what-are-jenkins-pipelines.md), [how do you use Jenkins shared libraries](./how-do-you-use-jenkins-shared-libraries.md), [how do you trigger a pipeline](./how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md), and [running and securing a Jenkins controller in production](./how-do-you-run-and-secure-a-jenkins-controller-in-production.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)
- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
