---
title: "What is Jenkins?"
id: 17
category: "CI/CD"
difficulty: "Beginner"
tags:
  - devops
  - cicd
  - interview-questions
---

# What is Jenkins?

**Short answer:** Jenkins is an open-source automation server for building CI/CD pipelines, extended by a very large plugin ecosystem and configured as code through declarative `Jenkinsfile` pipelines stored alongside the application.

## Detail

Jenkins runs a controller that schedules work onto agents - static VMs, Docker containers, or dynamically provisioned Kubernetes pods. Its longevity comes from two things: it runs anywhere, including fully on-premises behind a firewall, and its ~1,800 plugins integrate with essentially every tool an enterprise already owns.

Modern Jenkins practice:

- **Pipeline as code** - a `Jenkinsfile` in the repository, versioned with the app rather than clicked into the UI.
- **Declarative syntax** - a structured `pipeline { }` block, easier to read and validate than the older scripted Groovy.
- **Multibranch pipelines** - automatically discover branches and pull requests and run the pipeline for each.
- **Shared libraries** - common pipeline logic factored out and reused across hundreds of repositories.
- **Kubernetes plugin** - spin up a fresh agent pod per build, so builds are isolated and the fleet scales to zero.
- **Configuration as Code (JCasC)** - the controller's own configuration expressed in YAML.

The trade-off versus hosted options like GitHub Actions or GitLab CI is that you operate Jenkins yourself: upgrades, plugin compatibility, agent capacity, and security hardening are your responsibility.

## Example

```groovy
pipeline {
  agent { kubernetes { yamlFile 'build-pod.yaml' } }
  options { timeout(time: 30, unit: 'MINUTES'); disableConcurrentBuilds() }
  environment { IMAGE = "registry.example.com/app:${env.GIT_COMMIT}" }

  stages {
    stage('Test')  { steps { sh 'make test' } }
    stage('Build') { steps { sh "docker build -t ${IMAGE} ." } }
    stage('Push')  {
      steps {
        withCredentials([usernamePassword(credentialsId: 'registry',
              usernameVariable: 'U', passwordVariable: 'P')]) {
          sh 'echo $P | docker login -u $U --password-stdin registry.example.com'
          sh "docker push ${IMAGE}"
        }
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps { sh "kubectl set image deploy/app app=${IMAGE}" }
    }
  }
  post { always { junit 'reports/**/*.xml' }; failure { slackSend "Build ${env.BUILD_URL} failed" } }
}
```

## Interview tips

- Emphasise pipeline-as-code and shared libraries; UI-configured jobs are the anti-pattern.
- Know how credentials are handled (`withCredentials`, never plain environment variables in the Jenkinsfile).
- Be ready to compare Jenkins with GitHub Actions/GitLab CI on operational cost versus control.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
