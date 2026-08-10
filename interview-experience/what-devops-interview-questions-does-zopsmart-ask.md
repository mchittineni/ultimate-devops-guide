---
title: "What DevOps interview questions does ZopSmart ask?"
id: 395
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - zopsmart
  - cicd
  - docker
  - configuration-management
  - infrastructure-as-code
  - kubernetes
  - aws-engineering
  - linux-administration
  - version-control
---

# What DevOps interview questions does ZopSmart ask?

## Questions

**CI/CD and Jenkins**

- **Explain a CI/CD pipeline.**
- **Write a declarative pipeline for a Jenkins server.**
- **You use Jenkins as an open-source tool — which AWS service is available to implement a CI/CD pipeline instead?**

**Docker**

- **Write a Dockerfile and explain the keywords in it.**
- **What is the command to display running containers and stopped containers?**
- **What are the commands to remove Docker images and containers?**

**Ansible**

- **Explain Ansible and how it works.**
- **What is an Ansible playbook?**
- **Write an Ansible playbook that installs Docker on the nodes.**

**Terraform**

- **What does `terraform init` do?**
- **What does `terraform plan` do?**
- **Which Terraform commands do you know?**

**Kubernetes**

- **Which Kubernetes commands do you know?**
- **You use a Kubernetes cluster as an open-source tool — which AWS service is available to create a Kubernetes cluster?**
- **How do you implement authentication in a Kubernetes cluster?**

**AWS and networking**

- **What is an IAM role?**
- **What is VPC peering?**
- **What is the difference between EBS and EFS?**

**Build tooling, Git, and Linux**

- **What is the Maven lifecycle?**
- **Which Git commands do you use in daily tasks, and what is `git stash`?**
- **What is the command to change file permissions in Linux?**

## Example

```text
ZopSmart — DevOps Engineer (2 YOE), reported round
22 questions

  Docker                      3   write a Dockerfile + explain keywords,
                                  list running vs stopped, remove images
                                  and containers
  CI/CD and Jenkins           3   explain a pipeline, write a declarative
                                  Jenkinsfile, the AWS equivalent
  Ansible                     3   how it works, what a playbook is,
                                  write one that installs Docker
  Terraform                   3   init, plan, which commands you know
  Kubernetes                  3   commands, the AWS equivalent, authentication
  AWS and networking          3   IAM role, VPC peering, EBS vs EFS
  Build / Git / Linux         4   Maven lifecycle, daily Git commands,
                                  git stash, chmod

A JUNIOR ROUND THAT ASKS YOU TO WRITE
  At 2 years the questions are mostly definitions, but three of them —
  a Jenkinsfile, a Dockerfile, and an Ansible playbook — must be typed out.
  Practise writing all three from memory; that is where this round is decided.
```

```yaml
# The Ansible playbook they ask you to write. Idempotent, uses the
# distribution's own repo setup, and enables the service on boot.
- name: Install Docker on all nodes
  hosts: nodes
  become: true
  tasks:
    - name: Install prerequisites
      ansible.builtin.package:
        name: "{{ docker_prereqs }}"
        state: present

    - name: Install Docker engine
      ansible.builtin.package:
        name: docker-ce
        state: present

    - name: Ensure Docker is running and enabled on boot
      ansible.builtin.service:
        name: docker
        state: started
        enabled: true

    - name: Add the deploy user to the docker group
      ansible.builtin.user:
        name: "{{ deploy_user }}"
        groups: docker
        append: true
```

## Interview tips

- The three write-it-out questions are where a junior round is won or lost, so practise typing each from memory rather than describing it. For the **Jenkinsfile**, the declarative skeleton is `pipeline { agent { label '...' } environment { } stages { stage('Build') { steps { sh '...' } } } post { always { } failure { } } }` — and be ready to explain each block, because that is the standard follow-up: `agent` decides where it runs, `environment` injects variables at pipeline or stage scope, `stages` holds the work, and `post` runs cleanup and notification with `always`, `success`, and `failure` conditions. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- For the **Dockerfile**, write a multi-stage one even if they only asked for a simple one, and explain the keywords as you go: `FROM` sets the base image (pinned by tag or digest), `WORKDIR` sets the working directory, `COPY` brings files from the build context in, `RUN` executes a command creating a new layer, `ENV` sets runtime environment variables, `ARG` sets build-time ones, `EXPOSE` documents a port (it publishes nothing), `USER` drops from root, `ENTRYPOINT` is the executable and `CMD` supplies default arguments, and `HEALTHCHECK` defines liveness. Then add the ordering point that shows understanding: copy the dependency manifest and install dependencies _before_ copying source, so a code change reuses the cached dependency layer. See [what a Dockerfile is](../docker/what-is-dockerfile.md).
- The **Ansible playbook** answer must be idempotent, and saying so is the point of the question. Use the `package` and `service` modules with `state: present` and `state: started` plus `enabled: true` rather than shelling out to `apt-get install` — because a module is declarative and a `command` is not, so re-running the playbook changes nothing the second time. Mention that the `become: true` directive is how you gain root, and that in production you would use the official Docker role from Galaxy rather than hand-rolling the repository setup. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- The two "which AWS service instead" questions have direct answers plus a nuance worth adding. For CI/CD: **CodePipeline** for orchestration, with CodeBuild for builds and CodeDeploy for deployments — and say that CodePipeline is the managed equivalent to Jenkins with no server to patch, cheaper for AWS-only workflows but less flexible for hybrid or non-AWS targets. For Kubernetes: **EKS**, the managed control plane — and add what "managed" actually means, because that is the useful part: AWS runs and patches the API server and etcd, so you never snapshot etcd yourself, and you manage node groups (or Karpenter) plus add-ons. See [building a CI/CD pipeline with CodePipeline, CodeBuild, and CodeDeploy](../aws-engineering/how-do-you-build-a-ci-cd-pipeline-using-aws-codepipeline-codebuild-and-codedeploy.md) and [ECS versus EKS versus Fargate](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md).
- Kubernetes authentication is the deepest question in the round, so answer it in the three stages the API server actually uses: **authentication** — client certificates, bearer tokens including service-account tokens, or an OIDC provider for human users, with EKS mapping IAM identities via access entries or the `aws-auth` ConfigMap; **authorisation** — RBAC, with Roles and ClusterRoles bound to users, groups, or service accounts; and **admission control** — validating and mutating webhooks plus Pod Security Admission deciding what an authorised request may actually create. Say that Kubernetes has no user database of its own, which is why authentication is always delegated to certificates, tokens, or an external identity provider — that is the fact the question is really testing. See [how RBAC works in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md).
- `terraform init` and `terraform plan` should each get the full mechanism rather than one line. `init` reads the configuration, downloads provider plugins into `.terraform/`, initialises the backend and pulls remote state, installs modules, and writes or verifies the dependency lock file — so it is the command you run first and again whenever providers, modules, or the backend change. `plan` refreshes state against reality, compares it with the desired configuration, and prints the diff — creating nothing. Add the CI practice that shows maturity: `plan -out=tfplan` then `apply tfplan`, so what is applied is provably what was reviewed. For the "which commands do you know" question, group them rather than listing at random: lifecycle (`init`, `validate`, `plan`, `apply`, `destroy`), formatting and inspection (`fmt`, `show`, `output`, `graph`), state (`state list`, `state mv`, `state rm`, `import`, `force-unlock`), and workspaces. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).
- The Docker command questions have exact answers worth knowing verbatim: `docker ps` lists running containers and `docker ps -a` includes stopped ones (with `-q` for just IDs); `docker rm <container>` removes a container and `docker rmi <image>` removes an image, with `docker container prune`, `docker image prune -a`, and `docker system prune -a --volumes` for bulk cleanup. Add the two practical notes: you cannot remove an image while a container references it unless you force it, and `system prune --volumes` deletes unused volumes, so it is destructive and should never be run casually on a shared host.
- EBS versus EFS is an access-mode question, and framing it that way is stronger than listing features: EBS is a **zonal block device** attached to one instance at a time — so `ReadWriteOnce` in Kubernetes terms — formatted with a filesystem and offering low-latency provisioned IOPS; EFS is a **network filesystem** supporting `ReadWriteMany`, so many instances or Pods across availability zones can mount it simultaneously, at higher latency and cost but with elastic capacity and no sizing decision. Say the deciding question: does one workload need fast block storage (EBS) or do several need to share the same files (EFS)? Then add the Kubernetes consequence — an EBS-backed Pod cannot be rescheduled to another zone, which is a common source of `Pending` Pods.
- IAM role and VPC peering should each come with the reason they exist. A **role** is an identity that can be _assumed_, carrying policies and vending temporary credentials — so it is how you avoid long-lived access keys, whether for an EC2 instance via an instance profile, a Pod via IRSA, or a cross-account caller via `sts:AssumeRole`. **VPC peering** is a private, one-to-one connection between two VPCs over the AWS backbone, and the two facts that matter are that it is **not transitive** — so N VPCs need N(N-1)/2 peerings, which is why Transit Gateway exists — and that the CIDR ranges **must not overlap**. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md) and [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- The Maven lifecycle question has a precise answer and one distinction that earns the mark: the default phases in order are validate, compile, test, package, verify, install, deploy — and because the lifecycle is sequential, running a phase runs every phase before it. The distinction: `install` places the artefact in your **local** repository at `~/.m2/repository`, while `deploy` publishes it to the **remote** repository such as Nexus or Artifactory. Add that there are three lifecycles — `default`, `clean`, and `site` — which is why `mvn clean install` invokes two.
- For the daily Git commands question, group by intent rather than reciting: inspect (`status`, `log`, `diff`), record (`add`, `commit`), sync (`fetch`, `pull --rebase`, `push`), branch (`switch`, `branch`, `merge`, `rebase`), and recover (`stash`, `restore`, `reset`, `revert`, `reflog`). Then give `git stash` properly: it shelves uncommitted tracked changes so you get a clean working tree, `stash pop` reapplies and drops the entry while `stash apply` keeps it, `stash list` shows the stack, and `-u` is needed to include untracked files — which is the classic surprise. See [undoing changes in Git safely](../version-control/how-do-you-undo-changes-in-git-safely.md).
- `chmod` is the command, and the answer that stands out gives both notations plus the ownership counterpart: `chmod 755 file` in octal, or `chmod u+x,g-w file` symbolically, with `-R` for recursive — and `chown` for ownership, `chgrp` for group. Then the detail worth volunteering because it comes up in real work: SSH refuses to use a private key or `authorized_keys` with permissions that are too open, so `~/.ssh` must be `700` and the files `600`. See [basic Linux commands](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md).
- On "explain a CI/CD pipeline", give a real stage-by-stage flow rather than the acronyms: commit triggers build, unit tests, static analysis, dependency and image scanning, image built once and tagged with the Git SHA, pushed to a registry, deployed automatically to dev, smoke tests, then promotion to higher environments behind an approval. Say the principle that makes it correct — build once and promote the same artefact, changing only configuration — because rebuilding per environment means you never tested what you shipped. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md) and [continuous delivery versus continuous deployment](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md).
- At two years of experience the interviewer is calibrating breadth and honesty, not depth. Where you have not used something, say so and describe the nearest thing you have done — inventing experience invites a follow-up you cannot answer, and this round has enough questions that one honest gap costs very little.

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
