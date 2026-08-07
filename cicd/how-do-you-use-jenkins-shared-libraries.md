---
title: "How do you use Jenkins shared libraries?"
id: 268
category: "CI/CD"
difficulty: "Advanced"
tags:
  - devops
  - cicd
  - interview-questions
---

# How do you use Jenkins shared libraries?

**Short answer:** A shared library is a versioned Git repository of Groovy code that many Jenkinsfiles import, so pipeline logic is written once instead of copy-pasted into a hundred repositories. It has a fixed layout - `vars/` for the steps you call by name, `src/` for classes, `resources/` for non-Groovy files - and you load it with `@Library('name@version')` or configure it as an implicit global library.

## Detail

**The problem it solves.** Without a shared library, every service repository carries its own 200-line Jenkinsfile. Changing how you publish artefacts, or adding a mandatory security scan, means a pull request against every repository. With one, the Jenkinsfile shrinks to a handful of lines and the change lands in one place.

**The required layout** - Jenkins will not find your code otherwise:

```text
(root)
├── vars/                     # global variables/steps, callable by filename
│   ├── buildDockerImage.groovy
│   ├── deployToKubernetes.groovy
│   └── standardPipeline.groovy
├── src/                      # regular Groovy classes, package structure
│   └── com/acme/ci/Notifier.groovy
├── resources/                # static files loaded with libraryResource
│   └── com/acme/ci/pod-template.yaml
└── test/                     # unit tests (JenkinsPipelineUnit)
```

- **`vars/`** is the important one. A file `vars/buildDockerImage.groovy` defining `def call(Map config)` becomes a step you invoke as `buildDockerImage(image: 'api')` in any Jenkinsfile. Add a matching `buildDockerImage.txt` and the documentation appears in Jenkins' UI.
- **`src/`** holds real classes for anything with state or complex logic. Note these run under the Groovy sandbox and CPS transformation, which is why some ordinary Groovy - closures on collections, for instance - misbehaves. `@NonCPS` opts a method out, at the cost of not being able to call pipeline steps from it.
- **`resources/`** is fetched with `libraryResource 'com/acme/ci/pod-template.yaml'` - the standard way to ship YAML templates or scripts alongside the library.

**Loading and versioning.** `@Library('acme-pipelines@v2.3.0') _` (the trailing underscore is required - the annotation must attach to something). The version is any Git ref: a tag, branch, or commit SHA.

**Pin to tags in production.** Configuring the library to track `main` means every merge to the library instantly changes every pipeline in the organisation - a single bad commit can break all builds at once. Tag releases, have services reference a tag, and roll forward deliberately. Allowing `Modifiable default version` lets a team pin an older tag while you migrate.

**Trusted vs untrusted.** Libraries configured globally at the Jenkins level run **outside** the Groovy sandbox with full access to the controller - so they must live in a repository only platform engineers can write to. Folder-level libraries and `libraryResource`-loaded code are sandboxed. Treating the shared library repository as production infrastructure, with code review and branch protection, is a security answer interviewers look for.

**Testing.** A library that breaks every pipeline needs tests. JenkinsPipelineUnit lets you unit-test `vars/` steps on the JVM without a Jenkins instance; run it in the library's own CI, plus a smoke pipeline that exercises the library end to end before you tag a release.

**Where this fits in 2026.** Many teams have moved to GitHub Actions reusable workflows, GitLab CI `include:`, or templated pipelines - the same idea with less Groovy. Say that if asked about alternatives: shared libraries are the Jenkins answer to pipeline duplication, and the concept transfers directly.

## Example

```groovy
// vars/standardPipeline.groovy - one call gives a service its whole pipeline
def call(Map config = [:]) {
  pipeline {
    agent { kubernetes { yaml libraryResource('com/acme/ci/pod-template.yaml') } }

    options {
      timeout(time: 30, unit: 'MINUTES')
      buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    stages {
      stage('Build & Test') {
        steps { container('build') { sh 'make ci' } }
      }

      stage('Security') {
        parallel {
          stage('SCA')  { steps { container('build') { sh 'trivy fs --exit-code 1 --severity HIGH,CRITICAL .' } } }
          stage('SAST') { steps { container('build') { sh 'semgrep ci' } } }
        }
      }

      stage('Publish') {
        when { branch 'main' }
        steps {
          script {
            // Reuse another step from vars/ - composition, not duplication
            buildDockerImage(image: config.image, tag: env.GIT_COMMIT.take(7))
          }
        }
      }

      stage('Deploy') {
        when { branch 'main' }
        steps {
          script {
            deployToKubernetes(
              environment: 'staging',
              image: "${config.image}:${env.GIT_COMMIT.take(7)}"
            )
          }
        }
      }
    }

    post {
      failure { script { new com.acme.ci.Notifier(this).alert(config.slackChannel) } }
      always  { junit allowEmptyResults: true, testResults: '**/test-results/*.xml' }
    }
  }
}
```

```groovy
// Jenkinsfile in each service repository - this is the whole file
@Library('acme-pipelines@v2.3.0') _

standardPipeline(
  image: 'ghcr.io/acme/payments-api',
  slackChannel: '#payments-alerts'
)
```

## Interview tips

- Lead with the problem - pipeline logic duplicated across every repository - then the structure. The `vars/` versus `src/` distinction is the detail most often checked.
- Know that a file in `vars/` becomes a step named after the file, and that it needs `def call(...)`.
- Pinning to a tag rather than `main` is the operational answer that separates people who have run a shared library from people who have read the docs. Say what happens otherwise: one commit breaks every pipeline in the company.
- Mention that global libraries run outside the sandbox and therefore need a locked-down repository. It turns a CI question into a supply-chain answer.
- Expect "how do you test it?" - JenkinsPipelineUnit plus a smoke pipeline before tagging.
- If CPS or `@NonCPS` comes up, explain it simply: pipeline code is transformed so it can be paused and resumed, which breaks some ordinary Groovy; `@NonCPS` opts out but cannot call pipeline steps.
- Be ready to compare with GitHub Actions reusable workflows or GitLab `include:` - many interviewers now ask what you would use if you were not on Jenkins.

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
