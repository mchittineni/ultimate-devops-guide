---
title: "What DevOps interview questions does Belcan ask?"
id: 318
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - belcan
  - cicd
  - version-control
  - infrastructure-as-code
  - aws-engineering
  - scalability-and-high-availability
---

# What DevOps interview questions does Belcan ask?

## Questions

**Jenkins**

- **Write a Jenkins pipeline.**
- **What are the `agent`, `post`, and `environment` blocks for in a declarative pipeline?**
- **How do you take a complete backup of Jenkins, including jobs, configuration, and authentication settings?**
- **What are all the ways a Jenkins pipeline can be triggered?**
- **You have five Jenkins jobs and need to give other users view-only access to them. How do you configure that?**

**AWS**

- **How many load balancer types does AWS offer, and what is each one for?**
- **What is the difference between an Elastic IP and a public IP in AWS?**

**Git**

- **Write down the Git commands you use daily and explain what each one does.**
- **You have a local clone, you changed one file, and you want that change on the remote. Which commands do you run, in order?**
- **Explain `git stash`.**

**Terraform**

- **What is the Terraform state file, and what is it for?**
- **Write down a handful of Terraform commands and explain each one.**

## Example

```text
Belcan — DevOps Engineer (9 YOE), reported round
12 questions

  Jenkins                     5   write a pipeline, agent/post/environment,
                                  full backup, trigger types, view-only RBAC
  Git                         3   daily commands, local->remote flow, stash
  Terraform                   2   state file, commands explained
  AWS                         2   load balancer types, Elastic IP vs public IP

FORMAT NOTE
  Three questions say "write" or "write down". This is a whiteboard or
  shared-doc round — practise typing a Jenkinsfile from memory, not
  describing one.
```

```groovy
// The shape they expect, with all three blocks the follow-up asks about.
pipeline {
  agent { label 'linux' }                 // WHERE it runs
  environment { AWS_REGION = 'eu-west-1' } // available to every stage
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Build')    { steps { sh 'make build' } }
    stage('Test')     { steps { sh 'make test' } }
  }
  post {                                   // runs regardless of outcome
    always  { junit 'reports/*.xml' }
    failure { echo 'notify the team' }
  }
}
```

## Interview tips

- Write the `Jenkinsfile` declaratively and then explain the three blocks in one pass: `agent` decides where the work runs and can be set per stage, `environment` injects variables at pipeline or stage scope, and `post` runs cleanup and notifications with `always`, `success`, `failure`, and `unstable` conditions. Naming `post` conditions individually is what distinguishes a real answer. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- The Jenkins backup question has a specific answer: everything lives under `JENKINS_HOME`, so back up `config.xml`, the `jobs/` directory, `users/`, `secrets/`, `credentials.xml`, and the plugin list. Add that `secrets/` must be included or restored credentials will be undecryptable — that detail is the point of the question. Mention Configuration as Code as the better long-term answer, since it makes the controller reproducible from Git instead of from a tarball.
- View-only access for five jobs means the Role Strategy plugin: a project role whose pattern matches those job names, granting Overall Read plus Job Read and Job Discover, assigned to the users. Say that Jenkins' built-in matrix authorisation is global-only, which is why the plugin exists. See [Jenkins shared libraries](../cicd/how-do-you-use-jenkins-shared-libraries.md) for the related question about shared pipeline logic.
- List trigger types exhaustively because it is a completeness question: SCM polling, webhooks from the forge, `cron` schedules, upstream job completion, manual builds with parameters, remote API calls with a token, and pull-request events via multibranch scanning. Then add that webhooks are preferred over polling because polling scales badly.
- AWS load balancers are currently four: Application, Network, Gateway, and the legacy Classic. Give one sentence each and a scenario for the first two. See [layer 4 versus layer 7 load balancers](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md).
- Elastic IP versus public IP is really a question about stability: an auto-assigned public IP changes when the instance stops and starts, an Elastic IP is allocated to your account and persists until you release it. Add that Elastic IPs are chargeable when unattached, which is the cost follow-up.
- For the local-to-remote sequence, give it in order and say what each step does to which store: `git status`, `git add <file>` to stage, `git commit -m` to write the object, `git pull --rebase` to integrate remote work, then `git push`. Volunteering the `pull` before the `push` shows you have hit a rejected push before. See [handling merge conflicts](../version-control/how-to-handle-merge-conflicts-in-git.md).
- On the Terraform state file, cover what it stores (the mapping from configuration to real resource IDs plus attributes), where it belongs (remote backend, encrypted, versioned), why locking matters, and that it may contain secrets in plain text. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md) and [recovering a lost or corrupted state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
