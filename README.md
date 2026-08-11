<div align="center">

# ⚙️ Cloud, DevOps, Platform & SRE Guide

**507 questions across 40 topics - answered to the depth an interviewer actually expects.**

Role tracks: **DevOps** (junior → senior) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

Every answer gives you a short answer you can say out loud, the detail and trade-offs behind it, a runnable example, and the follow-ups to expect.

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)
![Questions](https://img.shields.io/badge/questions-507-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20110%20·%20🟡%20233%20·%20🔴%20164-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

[🌐 3D Knowledge Graph](https://mchittineni.github.io/ultimate-devops-guide/) · [Pick your role](#-pick-your-role) · [Browse topics](#-browse-all-topics) · [All questions](#-all-questions) · [How answers are structured](#-how-answers-are-structured) · [Contributing](./CONTRIBUTING.md)

⭐ Star the project if it helps you land the role.

</div>

---

## 🌐 3D DevOps Knowledge Graph

Explore the entire repository visually through our **Interactive 3D Telemetry Graph** deployed on GitHub Pages:

👉 **[Launch Interactive 3D Knowledge Graph](https://mchittineni.github.io/ultimate-devops-guide/)**

- **Visual Infrastructure Mapping**: Explore relationship edges connecting all 500+ questions across 40 topics.
- **Cross-Topic Concept Wikilinks**: Discover cross-cutting concepts between Docker, Kubernetes, CI/CD, IaC, and SRE.
- **Filterable Telemetry**: Filter nodes live by difficulty, domain group, or specific keywords.

---

## 🚀 Pick your role

Thirteen tracks, each a reading order rather than a pile of links. Start at the left and work right.

> **Interview in a fortnight?** Start with [Interview Experience](./interview-experience/README.md) - it covers the round structure, how to explain your project, how to handle scenario questions, and a checklist of what actually gets asked, cross-linked to every answer in this guide.

| 🎯 Target role                | Read in this order                                                                                                                                                                                                                                                                       |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Interviewing now**          | [Interview Experience](./interview-experience/README.md) → [Linux](./linux-administration/README.md) → [Version Control](./version-control/README.md) → [Docker](./docker/README.md) → [Kubernetes](./kubernetes/README.md) → [IaC](./infrastructure-as-code/README.md)                  |
| **Junior / Associate DevOps** | [Core Concepts](./core-devops-concepts/README.md) → [Docker](./docker/README.md) → [Linux](./linux-administration/README.md) → [Version Control](./version-control/README.md) → [Scripting](./scripting-and-automation/README.md) → [CI/CD](./cicd/README.md)                            |
| **DevSecOps Engineer**        | [DevSecOps](./devsecops/README.md) → [Security & Compliance](./security-and-compliance/README.md) → [Network Security](./network-security/README.md) → [CI/CD](./cicd/README.md)                                                                                                         |
| **SecOps Engineer**           | [SecOps](./secops/README.md) → [Network Security](./network-security/README.md) → [Incident Management](./incident-management/README.md) → [Security & Compliance](./security-and-compliance/README.md)                                                                                  |
| **SRE Engineer**              | [SRE](./site-reliability-engineering/README.md) → [SLO Engineering](./slo-engineering/README.md) → [Incident Management](./incident-management/README.md) → [Infrastructure Monitoring](./infrastructure-monitoring/README.md) → [Metrics](./devops-metrics-and-kpis/README.md)          |
| **SLO Engineer**              | [SLO Engineering](./slo-engineering/README.md) → [SRE](./site-reliability-engineering/README.md) → [Infrastructure Monitoring](./infrastructure-monitoring/README.md) → [Monitoring & Logging](./monitoring-and-logging/README.md)                                                       |
| **SLA Engineer**              | [SLA Management](./sla-management/README.md) → [SLO Engineering](./slo-engineering/README.md) → [Scalability & HA](./scalability-and-high-availability/README.md) → [Backup & DR](./backup-and-disaster-recovery/README.md)                                                              |
| **AWS Engineer**              | [AWS Engineering](./aws-engineering/README.md) → [Cloud Engineering](./cloud-engineering/README.md) → [IaC](./infrastructure-as-code/README.md) → [Kubernetes](./kubernetes/README.md) → [Cost](./cloud-cost-optimization/README.md)                                                     |
| **Azure Engineer**            | [Azure Engineering](./azure-engineering/README.md) → [Cloud Engineering](./cloud-engineering/README.md) → [IaC](./infrastructure-as-code/README.md) → [Kubernetes](./kubernetes/README.md) → [Cost](./cloud-cost-optimization/README.md)                                                 |
| **GCP Engineer**              | [GCP Engineering](./gcp-engineering/README.md) → [Cloud Engineering](./cloud-engineering/README.md) → [IaC](./infrastructure-as-code/README.md) → [Kubernetes](./kubernetes/README.md) → [Cost](./cloud-cost-optimization/README.md)                                                     |
| **Cloud Engineer**            | [Cloud Engineering](./cloud-engineering/README.md) → [Cloud Platforms](./cloud-platforms/README.md) → [IaC](./infrastructure-as-code/README.md) → [Cloud Migration](./cloud-migration/README.md) → [Scalability & HA](./scalability-and-high-availability/README.md)                     |
| **Platform Engineer**         | [Platform Engineering](./platform-engineering/README.md) → [Kubernetes](./kubernetes/README.md) → [Orchestration Advanced](./container-orchestration-advanced/README.md) → [Tools & Automation](./devops-tools-and-automation/README.md) → [Advanced](./advanced-devops-cloud/README.md) |
| **Senior / Lead**             | [Cloud Native](./cloud-native-architecture/README.md) → [Platform Engineering](./platform-engineering/README.md) → [Cost](./cloud-cost-optimization/README.md) → [Culture](./devops-culture-and-practices/README.md) → [Advanced](./advanced-devops-cloud/README.md)                     |

---

## 📚 Browse all topics

Grouped by theme, with question counts and difficulty mix. Click a topic to open its index, which opens with what interviewers probe there.

<!-- STATS:START -->

**507 questions** across **40 topics** - 🟢 110 Beginner · 🟡 233 Intermediate · 🔴 164 Advanced

### 🧱 Foundations

| Topic                                                                | Questions | 🟢  | 🟡  | 🔴  | What it covers                                                                                   |
| -------------------------------------------------------------------- | --------- | --- | --- | --- | ------------------------------------------------------------------------------------------------ |
| **[Core DevOps Concepts](./core-devops-concepts/README.md)**         | 6         | 4   | 1   | 1   | what DevOps actually changes, why it exists, and how CI, continuous delivery, and continuous…    |
| **[Linux Administration](./linux-administration/README.md)**         | 13        | 7   | 5   | 1   | The operating system under everything - commands, shell scripting, systemd, service management,… |
| **[Version Control](./version-control/README.md)**                   | 10        | 4   | 5   | 1   | Git mechanics and the branching models teams actually argue about, including how to resolve…     |
| **[Scripting and Automation](./scripting-and-automation/README.md)** | 6         | 1   | 4   | 1   | The scripting layer under every pipeline - defensive Bash for orchestration, and Python for…     |

### 📦 Containers and Kubernetes

| Topic                                                                                | Questions | 🟢  | 🟡  | 🔴  | What it covers                                                                                   |
| ------------------------------------------------------------------------------------ | --------- | --- | --- | --- | ------------------------------------------------------------------------------------------------ |
| **[Docker](./docker/README.md)**                                                     | 15        | 6   | 7   | 2   | Container fundamentals - images versus containers, Dockerfile authoring, Compose, and the…       |
| **[Kubernetes](./kubernetes/README.md)**                                             | 27        | 3   | 18  | 6   | The control plane, the workload objects you touch daily, and the networking abstractions that…   |
| **[Container Orchestration Advanced](./container-orchestration-advanced/README.md)** | 14        | 1   | 4   | 9   | Beyond Deployments - StatefulSets, DaemonSets, Helm packaging, Istio, and the container runtime… |

### 🔁 Delivery and Automation

| Topic                                                                      | Questions | 🟢  | 🟡  | 🔴  | What it covers                                                                                      |
| -------------------------------------------------------------------------- | --------- | --- | --- | --- | --------------------------------------------------------------------------------------------------- |
| **[CI/CD](./cicd/README.md)**                                              | 20        | 2   | 14  | 4   | Pipeline design, Jenkins and GitLab CI mechanics, and the delivery-versus-deployment distinction…   |
| **[Infrastructure as Code](./infrastructure-as-code/README.md)**           | 16        | 4   | 8   | 4   | Declarative infrastructure with Terraform and Ansible - state, providers, idempotency, and where…   |
| **[Configuration Management](./configuration-management/README.md)**       | 11        | 1   | 9   | 1   | Keeping fleets consistent with Puppet, Chef, Ansible, and Salt - push versus pull, agent versus…    |
| **[DevOps Tools and Automation](./devops-tools-and-automation/README.md)** | 9         | 2   | 6   | 1   | GitOps with Argo CD, Tekton pipelines, and the deployment strategies used to ship without downtime. |

### ☁️ Cloud Providers

| Topic                                                              | Questions | 🟢  | 🟡  | 🔴  | What it covers                                                                                    |
| ------------------------------------------------------------------ | --------- | --- | --- | --- | ------------------------------------------------------------------------------------------------- |
| **[Cloud Platforms](./cloud-platforms/README.md)**                 | 7         | 5   | 1   | 1   | Cloud service models and the three major providers - enough breadth to discuss AWS, Azure, and…   |
| **[Cloud Cost Optimization](./cloud-cost-optimization/README.md)** | 8         | 2   | 5   | 1   | Reserved and spot capacity, tagging discipline, and the reports that turn a cloud bill into…      |
| **[Cloud Migration](./cloud-migration/README.md)**                 | 8         | 1   | 4   | 3   | Assessment, the 6 Rs, application modernization, and the tooling that moves workloads without…    |
| **[AWS Engineering](./aws-engineering/README.md)**                 | 26        | 6   | 13  | 7   | VPC design, IAM policy evaluation, ECS/EKS/Fargate, Auto Scaling with load balancers, S3 storage… |
| **[Azure Engineering](./azure-engineering/README.md)**             | 13        | 1   | 10  | 2   | the resource hierarchy, Entra ID and RBAC, VNet and private endpoint design, AKS, Bicep, Azure…   |
| **[GCP Engineering](./gcp-engineering/README.md)**                 | 9         | 1   | 7   | 1   | resource hierarchy and org policies, IAM without service-account keys, the global VPC, GKE…       |
| **[Cloud Engineering](./cloud-engineering/README.md)**             | 8         | 1   | 4   | 3   | landing zones, hybrid connectivity, least-privilege identity, multi-region resilience,…           |

### 🏗️ Architecture and Scale

| Topic                                                                                  | Questions | 🟢  | 🟡  | 🔴  | What it covers                                                                                   |
| -------------------------------------------------------------------------------------- | --------- | --- | --- | --- | ------------------------------------------------------------------------------------------------ |
| **[Scalability and High Availability](./scalability-and-high-availability/README.md)** | 9         | 4   | 2   | 3   | scaling dimensions, load balancing, auto scaling, and recovery objectives.                       |
| **[Cloud Native Architecture](./cloud-native-architecture/README.md)**                 | 8         | 1   | 4   | 3   | Microservices, service mesh, event-driven design, and the Twelve-Factor principles that make…    |
| **[Performance Testing](./performance-testing/README.md)**                             | 6         | 3   | 2   | 1   | Load, stress, soak, and spike testing - how to design them, which tools to use, and how to read… |
| **[API Gateway and Service Mesh](./api-gateway-and-service-mesh/README.md)**           | 8         | 3   | 3   | 2   | gateway responsibilities, security, rate limiting, and documentation as a first-class artifact.  |
| **[Serverless Architecture](./serverless-architecture/README.md)**                     | 8         | 4   | 3   | 1   | Functions as a service, the operational model behind them, and the design patterns that keep…    |
| **[Database Management in DevOps](./database-management-in-devops/README.md)**         | 8         | 1   | 4   | 3   | version control, migration tooling, backup strategy, and performance tuning.                     |

### 📈 Reliability and Operations

| Topic                                                                              | Questions | 🟢  | 🟡  | 🔴  | What it covers                                                                                       |
| ---------------------------------------------------------------------------------- | --------- | --- | --- | --- | ---------------------------------------------------------------------------------------------------- |
| **[Monitoring and Logging](./monitoring-and-logging/README.md)**                   | 9         | 4   | 4   | 1   | Metrics, logs, and the toolchain - Prometheus, Grafana, and the ELK stack - plus the conceptual…     |
| **[Backup and Disaster Recovery](./backup-and-disaster-recovery/README.md)**       | 7         | 4   | 2   | 1   | Backup types, RPO/RTO targets, business continuity planning, and the discipline of testing restores. |
| **[Site Reliability Engineering (SRE)](./site-reliability-engineering/README.md)** | 9         | 1   | 6   | 2   | SLIs, SLOs, error budgets, and the systematic elimination of toil.                                   |
| **[DevOps Metrics and KPIs](./devops-metrics-and-kpis/README.md)**                 | 6         | 3   | 2   | 1   | The four DORA metrics and the measurement habits that keep them honest.                              |
| **[Incident Management](./incident-management/README.md)**                         | 7         | 2   | 3   | 2   | response plans, severity levels, on-call practice, and blameless learning.                           |
| **[Infrastructure Monitoring](./infrastructure-monitoring/README.md)**             | 7         | 2   | 4   | 1   | Host and platform monitoring, APM, log management, and the practices that keep dashboards and…       |
| **[SLO Engineering](./slo-engineering/README.md)**                                 | 8         | 1   | 3   | 4   | choosing targets, burn-rate alerting, correct latency SLIs, error budget policies, and SLOs for…     |
| **[SLA Management](./sla-management/README.md)**                                   | 7         | 2   | 4   | 1   | SLA versus SLO versus OLA, downtime and composite availability arithmetic, contract clauses,…        |

### 🔐 Security

| Topic                                                              | Questions | 🟢  | 🟡  | 🔴  | What it covers                                                                                    |
| ------------------------------------------------------------------ | --------- | --- | --- | --- | ------------------------------------------------------------------------------------------------- |
| **[Security and Compliance](./security-and-compliance/README.md)** | 6         | 1   | 3   | 2   | DevSecOps practice, infrastructure and container hardening, and compliance expressed as code.     |
| **[Network Security](./network-security/README.md)**               | 12        | 4   | 6   | 2   | Zero trust, TLS, web application firewalls, and segmentation - the controls that protect traffic… |
| **[DevSecOps](./devsecops/README.md)**                             | 12        | 1   | 7   | 4   | scanning layers, SBOMs and supply-chain provenance, image signing, secretless pipelines, and…     |
| **[SecOps and Threat Detection](./secops/README.md)**              | 8         | 2   | 4   | 2   | SOC workflow, SIEM and normalisation, detection engineering, MITRE ATT&CK coverage, threat…       |

### 🧭 Platform and Leadership

| Topic                                                                        | Questions | 🟢  | 🟡  | 🔴  | What it covers                                                                                    |
| ---------------------------------------------------------------------------- | --------- | --- | --- | --- | ------------------------------------------------------------------------------------------------- |
| **[DevOps Culture and Practices](./devops-culture-and-practices/README.md)** | 6         | 4   | 1   | 1   | The human half of DevOps - shared ownership, blamelessness, knowledge sharing, and collaboration… |
| **[Advanced DevOps & Cloud](./advanced-devops-cloud/README.md)**             | 20        | 5   | 8   | 7   | platform engineering, FinOps, policy as code, chaos engineering, observability, and progressive…  |
| **[Platform Engineering](./platform-engineering/README.md)**                 | 14        | 1   | 5   | 8   | IDPs, golden paths, Backstage, Crossplane, self-service environments, adoption metrics, and safe… |

### 🎤 Interview Prep

| Topic                                                        | Questions | 🟢  | 🟡  | 🔴  | What it covers                                                                            |
| ------------------------------------------------------------ | --------- | --- | --- | --- | ----------------------------------------------------------------------------------------- |
| **[Interview Experience](./interview-experience/README.md)** | 96        | 5   | 28  | 63  | How the interview itself works - the round structure, explaining your project, answering… |

<!-- STATS:END -->

---

## 📋 All questions

Every question in the repository, collapsed by topic - open only the ones you are studying.

<!-- TOC:START -->

### 🧱 Foundations

_35 questions_

<details>
<summary><b>Core DevOps Concepts</b> · 6 questions · 🟢 4 🟡 1 🔴 1</summary>

[Open the Core DevOps Concepts index →](./core-devops-concepts/README.md)

| No. | Question                                                                                                                                                    | Difficulty      |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 1   | [What is DevOps?](./core-devops-concepts/what-is-devops.md)                                                                                                 | 🟢 Beginner     |
| 2   | [What are the benefits of DevOps?](./core-devops-concepts/what-are-the-benefits-of-devops.md)                                                               | 🟢 Beginner     |
| 3   | [What is Continuous Integration?](./core-devops-concepts/what-is-continuous-integration.md)                                                                 | 🟢 Beginner     |
| 4   | [What is Continuous Delivery?](./core-devops-concepts/what-is-continuous-delivery.md)                                                                       | 🟢 Beginner     |
| 5   | [What is Continuous Deployment?](./core-devops-concepts/what-is-continuous-deployment.md)                                                                   | 🟡 Intermediate |
| 285 | [How do you take a monthly release process to daily deployments?](./core-devops-concepts/how-do-you-take-a-monthly-release-process-to-daily-deployments.md) | 🔴 Advanced     |

</details>

<details>
<summary><b>Linux Administration</b> · 13 questions · 🟢 7 🟡 5 🔴 1</summary>

[Open the Linux Administration index →](./linux-administration/README.md)

| No. | Question                                                                                                                                                                                    | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 41  | [What are the basic Linux commands every DevOps engineer should know?](./linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md)                       | 🟢 Beginner     |
| 42  | [What is Shell Scripting?](./linux-administration/what-is-shell-scripting.md)                                                                                                               | 🟢 Beginner     |
| 43  | [What is systemd?](./linux-administration/what-is-systemd.md)                                                                                                                               | 🟡 Intermediate |
| 44  | [How do you manage services in Linux?](./linux-administration/how-do-you-manage-services-in-linux.md)                                                                                       | 🟢 Beginner     |
| 45  | [What is Linux File System Hierarchy?](./linux-administration/what-is-linux-file-system-hierarchy.md)                                                                                       | 🟢 Beginner     |
| 238 | [How do you troubleshoot SSH failures, high CPU, and disk space on Linux servers?](./linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md) | 🟢 Beginner     |
| 265 | [How do you analyse logs and text files with grep, awk, and sed?](./linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md)                                   | 🟡 Intermediate |
| 295 | [How do you debug a Linux performance problem from first principles?](./linux-administration/how-do-you-debug-a-linux-performance-problem-from-first-principles.md)                         | 🔴 Advanced     |
| 494 | [What is the difference between a hard link and a soft link?](./linux-administration/what-is-the-difference-between-a-hard-link-and-a-soft-link.md)                                         | 🟢 Beginner     |
| 495 | [Walk through the Linux boot process](./linux-administration/walk-through-the-linux-boot-process.md)                                                                                        | 🟡 Intermediate |
| 496 | [How do you manage disks, filesystems, and LVM on Linux?](./linux-administration/how-do-you-manage-disks-filesystems-and-lvm-on-linux.md)                                                   | 🟡 Intermediate |
| 497 | [How do you schedule work with cron and systemd timers?](./linux-administration/how-do-you-schedule-work-with-cron-and-systemd-timers.md)                                                   | 🟢 Beginner     |
| 498 | [How do you inspect and manage Linux processes, signals, and resource limits?](./linux-administration/how-do-you-inspect-and-manage-linux-processes-signals-and-resource-limits.md)         | 🟡 Intermediate |

</details>

<details>
<summary><b>Version Control</b> · 10 questions · 🟢 4 🟡 5 🔴 1</summary>

[Open the Version Control index →](./version-control/README.md)

| No. | Question                                                                                                                                                                             | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 46  | [What is Git?](./version-control/what-is-git.md)                                                                                                                                     | 🟢 Beginner     |
| 47  | [What is Git Branching Strategy?](./version-control/what-is-git-branching-strategy.md)                                                                                               | 🟡 Intermediate |
| 48  | [What is Git Flow?](./version-control/what-is-git-flow.md)                                                                                                                           | 🟡 Intermediate |
| 49  | [What is Trunk Based Development?](./version-control/what-is-trunk-based-development.md)                                                                                             | 🟡 Intermediate |
| 50  | [How to handle merge conflicts in Git?](./version-control/how-to-handle-merge-conflicts-in-git.md)                                                                                   | 🟢 Beginner     |
| 254 | [How do you use Git hooks for automated linting, testing, and commit validation?](./version-control/how-do-you-use-git-hooks-for-automated-linting-testing-and-commit-validation.md) | 🟢 Beginner     |
| 263 | [What is the difference between git merge, rebase, and cherry-pick?](./version-control/what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md)                           | 🟡 Intermediate |
| 264 | [How do you undo changes in Git safely?](./version-control/how-do-you-undo-changes-in-git-safely.md)                                                                                 | 🟡 Intermediate |
| 305 | [How do you recover from a bad Git history rewrite?](./version-control/how-do-you-recover-from-a-bad-git-history-rewrite.md)                                                         | 🔴 Advanced     |
| 499 | [What is the difference between git fetch, git pull, and git clone?](./version-control/what-is-the-difference-between-git-fetch-git-pull-and-git-clone.md)                           | 🟢 Beginner     |

</details>

<details>
<summary><b>Scripting and Automation</b> · 6 questions · 🟢 1 🟡 4 🔴 1</summary>

[Open the Scripting and Automation index →](./scripting-and-automation/README.md)

| No. | Question                                                                                                                                                                      | Difficulty      |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 266 | [How do you write a production-grade Bash script?](./scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)                                             | 🟡 Intermediate |
| 267 | [What do you use Python for as a DevOps engineer?](./scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md)                                             | 🟡 Intermediate |
| 301 | [When do you use Bash and when do you use Python?](./scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md)                                             | 🟢 Beginner     |
| 302 | [How do you turn a pile of ad hoc scripts into maintainable automation?](./scripting-and-automation/how-do-you-turn-a-pile-of-ad-hoc-scripts-into-maintainable-automation.md) | 🔴 Advanced     |
| 502 | [What Bash scripting exercises come up in DevOps interviews?](./scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)                       | 🟡 Intermediate |
| 503 | [What Python exercises come up in DevOps interviews?](./scripting-and-automation/what-python-exercises-come-up-in-devops-interviews.md)                                       | 🟡 Intermediate |

</details>

### 📦 Containers and Kubernetes

_56 questions_

<details>
<summary><b>Docker</b> · 15 questions · 🟢 6 🟡 7 🔴 2</summary>

[Open the Docker index →](./docker/README.md)

| No. | Question                                                                                                                                                                  | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 6   | [What is Docker?](./docker/what-is-docker.md)                                                                                                                             | 🟢 Beginner     |
| 7   | [What is the difference between Docker Image and Docker Container?](./docker/what-is-the-difference-between-docker-image-and-docker-container.md)                         | 🟢 Beginner     |
| 8   | [What is Dockerfile?](./docker/what-is-dockerfile.md)                                                                                                                     | 🟢 Beginner     |
| 9   | [What is Docker Compose?](./docker/what-is-docker-compose.md)                                                                                                             | 🟢 Beginner     |
| 10  | [Explain Docker Architecture](./docker/explain-docker-architecture.md)                                                                                                    | 🟡 Intermediate |
| 252 | [What are Docker network types (Bridge, Host, Overlay, Macvlan)?](./docker/what-are-docker-network-types-bridge-host-overlay-macvlan.md)                                  | 🟡 Intermediate |
| 260 | [How do you reduce Docker image size and build time?](./docker/how-do-you-reduce-docker-image-size-and-build-time.md)                                                     | 🟡 Intermediate |
| 291 | [How do namespaces, cgroups, and capabilities isolate a container?](./docker/how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md)                           | 🔴 Advanced     |
| 415 | [How do you troubleshoot Docker networking between containers?](./docker/how-do-you-troubleshoot-docker-networking-between-containers.md)                                 | 🟡 Intermediate |
| 416 | [Why does a container fail to start with a permission denied error?](./docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)                       | 🟡 Intermediate |
| 437 | [What is the difference between CMD and ENTRYPOINT in a Dockerfile?](./docker/what-is-the-difference-between-cmd-and-entrypoint-in-a-dockerfile.md)                       | 🟡 Intermediate |
| 438 | [What is the difference between the COPY and ADD instructions in a Dockerfile?](./docker/what-is-the-difference-between-the-copy-and-add-instructions-in-a-dockerfile.md) | 🟢 Beginner     |
| 439 | [How does Docker layer caching work?](./docker/how-does-docker-layer-caching-work.md)                                                                                     | 🟡 Intermediate |
| 440 | [What is the difference between a bind mount and a volume in Docker?](./docker/what-is-the-difference-between-a-bind-mount-and-a-volume-in-docker.md)                     | 🟢 Beginner     |
| 441 | [How do you harden a container image and a Dockerfile?](./docker/how-do-you-harden-a-container-image-and-a-dockerfile.md)                                                 | 🔴 Advanced     |

</details>

<details>
<summary><b>Kubernetes</b> · 27 questions · 🟢 3 🟡 18 🔴 6</summary>

[Open the Kubernetes index →](./kubernetes/README.md)

| No. | Question                                                                                                                                                                                     | Difficulty      |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 11  | [What is Kubernetes?](./kubernetes/what-is-kubernetes.md)                                                                                                                                    | 🟢 Beginner     |
| 12  | [What are the main components of Kubernetes architecture?](./kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)                                                          | 🟡 Intermediate |
| 13  | [What is a Pod in Kubernetes?](./kubernetes/what-is-a-pod-in-kubernetes.md)                                                                                                                  | 🟢 Beginner     |
| 14  | [What is a Service in Kubernetes?](./kubernetes/what-is-a-service-in-kubernetes.md)                                                                                                          | 🟢 Beginner     |
| 15  | [Explain the difference between Docker Swarm and Kubernetes](./kubernetes/explain-the-difference-between-docker-swarm-and-kubernetes.md)                                                     | 🟡 Intermediate |
| 234 | [How do you troubleshoot a Pod stuck in Pending or CrashLoopBackOff?](./kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md)                                    | 🟡 Intermediate |
| 255 | [How do liveness, readiness, and startup probes differ?](./kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md)                                                                | 🟡 Intermediate |
| 256 | [How do you control which node a Pod runs on?](./kubernetes/how-do-you-control-which-node-a-pod-runs-on.md)                                                                                  | 🟡 Intermediate |
| 257 | [How does RBAC work in Kubernetes?](./kubernetes/how-does-rbac-work-in-kubernetes.md)                                                                                                        | 🟡 Intermediate |
| 258 | [How do you autoscale workloads and nodes in Kubernetes?](./kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md)                                                            | 🔴 Advanced     |
| 259 | [How do you expose an application running in Kubernetes to the outside world?](./kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md)                  | 🟡 Intermediate |
| 403 | [How do you troubleshoot a Kubernetes Service that has no endpoints?](./kubernetes/how-do-you-troubleshoot-a-kubernetes-service-that-has-no-endpoints.md)                                    | 🟡 Intermediate |
| 404 | [How do you debug DNS resolution failures inside a Kubernetes cluster?](./kubernetes/how-do-you-debug-dns-resolution-failures-inside-a-kubernetes-cluster.md)                                | 🟡 Intermediate |
| 405 | [How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?](./kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md) | 🔴 Advanced     |
| 406 | [How do you debug a Kubernetes Ingress that is not routing traffic?](./kubernetes/how-do-you-debug-a-kubernetes-ingress-that-is-not-routing-traffic.md)                                      | 🟡 Intermediate |
| 407 | [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](./kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)                          | 🟡 Intermediate |
| 408 | [How do you troubleshoot a Kubernetes Job or CronJob that never completes?](./kubernetes/how-do-you-troubleshoot-a-kubernetes-job-or-cronjob-that-never-completes.md)                        | 🟡 Intermediate |
| 409 | [How do you handle node pressure and Pod evictions in Kubernetes?](./kubernetes/how-do-you-handle-node-pressure-and-pod-evictions-in-kubernetes.md)                                          | 🔴 Advanced     |
| 410 | [How do you perform and roll back a rolling update in Kubernetes?](./kubernetes/how-do-you-perform-and-roll-back-a-rolling-update-in-kubernetes.md)                                          | 🟡 Intermediate |
| 442 | [What is the difference between a ConfigMap and a Secret in Kubernetes?](./kubernetes/what-is-the-difference-between-a-configmap-and-a-secret-in-kubernetes.md)                              | 🟡 Intermediate |
| 443 | [How does persistent storage work in Kubernetes?](./kubernetes/how-does-persistent-storage-work-in-kubernetes.md)                                                                            | 🟡 Intermediate |
| 444 | [How do requests, limits, and QoS classes work in Kubernetes?](./kubernetes/how-do-requests-limits-and-qos-classes-work-in-kubernetes.md)                                                    | 🟡 Intermediate |
| 445 | [What are init containers and sidecar containers in Kubernetes?](./kubernetes/what-are-init-containers-and-sidecar-containers-in-kubernetes.md)                                              | 🟡 Intermediate |
| 446 | [What is a PodDisruptionBudget and when do you need one?](./kubernetes/what-is-a-poddisruptionbudget-and-when-do-you-need-one.md)                                                            | 🔴 Advanced     |
| 447 | [How does Pod networking and service discovery work in Kubernetes?](./kubernetes/how-does-pod-networking-and-service-discovery-work-in-kubernetes.md)                                        | 🔴 Advanced     |
| 448 | [What happens when a Kubernetes control-plane node or etcd fails?](./kubernetes/what-happens-when-a-kubernetes-control-plane-node-or-etcd-fails.md)                                          | 🔴 Advanced     |
| 449 | [How do you troubleshoot a Kubernetes node that is NotReady?](./kubernetes/how-do-you-troubleshoot-a-kubernetes-node-that-is-notready.md)                                                    | 🟡 Intermediate |

</details>

<details>
<summary><b>Container Orchestration Advanced</b> · 14 questions · 🟢 1 🟡 4 🔴 9</summary>

[Open the Container Orchestration Advanced index →](./container-orchestration-advanced/README.md)

| No. | Question                                                                                                                                                                              | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 81  | [What are StatefulSets in Kubernetes?](./container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md)                                                                     | 🔴 Advanced     |
| 82  | [What are DaemonSets in Kubernetes?](./container-orchestration-advanced/what-are-daemonsets-in-kubernetes.md)                                                                         | 🟡 Intermediate |
| 83  | [What is Helm?](./container-orchestration-advanced/what-is-helm.md)                                                                                                                   | 🟡 Intermediate |
| 84  | [What is Istio?](./container-orchestration-advanced/what-is-istio.md)                                                                                                                 | 🔴 Advanced     |
| 85  | [What is Container Runtime Interface (CRI)?](./container-orchestration-advanced/what-is-container-runtime-interface-cri.md)                                                           | 🔴 Advanced     |
| 284 | [What is container orchestration and why do you need it?](./container-orchestration-advanced/what-is-container-orchestration-and-why-do-you-need-it.md)                               | 🟢 Beginner     |
| 411 | [How do you upgrade a production Kubernetes cluster with zero downtime?](./container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md) | 🔴 Advanced     |
| 412 | [How do you troubleshoot a failed Helm release?](./container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)                                                 | 🟡 Intermediate |
| 413 | [How do you run and scale a stateful application on Kubernetes?](./container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)                 | 🔴 Advanced     |
| 414 | [How do you run an application across multiple Kubernetes clusters?](./container-orchestration-advanced/how-do-you-run-an-application-across-multiple-kubernetes-clusters.md)         | 🔴 Advanced     |
| 450 | [What is inside a Helm chart, and how do you customise one?](./container-orchestration-advanced/what-is-inside-a-helm-chart-and-how-do-you-customise-one.md)                          | 🟡 Intermediate |
| 451 | [How do you back up and restore a Kubernetes cluster?](./container-orchestration-advanced/how-do-you-back-up-and-restore-a-kubernetes-cluster.md)                                     | 🔴 Advanced     |
| 452 | [What are CustomResourceDefinitions and operators in Kubernetes?](./container-orchestration-advanced/what-are-customresourcedefinitions-and-operators-in-kubernetes.md)               | 🔴 Advanced     |
| 453 | [How do you run a multi-tenant Kubernetes cluster?](./container-orchestration-advanced/how-do-you-run-a-multi-tenant-kubernetes-cluster.md)                                           | 🔴 Advanced     |

</details>

### 🔁 Delivery and Automation

_56 questions_

<details>
<summary><b>CI/CD</b> · 20 questions · 🟢 2 🟡 14 🔴 4</summary>

[Open the CI/CD index →](./cicd/README.md)

| No. | Question                                                                                                                                                                            | Difficulty      |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 16  | [What is CI/CD Pipeline?](./cicd/what-is-ci-cd-pipeline.md)                                                                                                                         | 🟢 Beginner     |
| 17  | [What is Jenkins?](./cicd/what-is-jenkins.md)                                                                                                                                       | 🟢 Beginner     |
| 18  | [What are Jenkins Pipelines?](./cicd/what-are-jenkins-pipelines.md)                                                                                                                 | 🟡 Intermediate |
| 19  | [What is GitLab CI?](./cicd/what-is-gitlab-ci.md)                                                                                                                                   | 🟡 Intermediate |
| 20  | [What is the difference between Continuous Delivery and Continuous Deployment?](./cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)             | 🟡 Intermediate |
| 237 | [How do you prevent and handle secret leaks in CI/CD pipelines?](./cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md)                                           | 🟡 Intermediate |
| 268 | [How do you use Jenkins shared libraries?](./cicd/how-do-you-use-jenkins-shared-libraries.md)                                                                                       | 🔴 Advanced     |
| 396 | [How do you speed up a slow CI/CD pipeline?](./cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)                                                                                   | 🟡 Intermediate |
| 397 | [Why does a build pass locally but fail in CI?](./cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)                                                                             | 🟡 Intermediate |
| 398 | [How do you deal with flaky tests in a CI pipeline?](./cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)                                                                   | 🟡 Intermediate |
| 399 | [How do you promote a release across dev, staging, and production?](./cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)                                       | 🟡 Intermediate |
| 400 | [How do you design CI/CD for a microservices architecture?](./cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)                                                     | 🔴 Advanced     |
| 401 | [How do you keep dependencies up to date without breaking the build?](./cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)                                 | 🟡 Intermediate |
| 402 | [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](./cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md) | 🟡 Intermediate |
| 454 | [What is the difference between a declarative and a scripted Jenkins pipeline?](./cicd/what-is-the-difference-between-a-declarative-and-a-scripted-jenkins-pipeline.md)             | 🟡 Intermediate |
| 455 | [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](./cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)            | 🟡 Intermediate |
| 456 | [How do you run and secure a Jenkins controller in production?](./cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)                                             | 🔴 Advanced     |
| 457 | [How do you write an efficient and secure GitHub Actions workflow?](./cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)                                     | 🟡 Intermediate |
| 458 | [How do you integrate SonarQube and quality gates into a pipeline?](./cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)                                     | 🟡 Intermediate |
| 459 | [How do you scale CI/CD across many services and teams?](./cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)                                                           | 🔴 Advanced     |

</details>

<details>
<summary><b>Infrastructure as Code</b> · 16 questions · 🟢 4 🟡 8 🔴 4</summary>

[Open the Infrastructure as Code index →](./infrastructure-as-code/README.md)

| No. | Question                                                                                                                                                                                | Difficulty      |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 26  | [What is Infrastructure as Code?](./infrastructure-as-code/what-is-infrastructure-as-code.md)                                                                                           | 🟢 Beginner     |
| 27  | [What is Terraform?](./infrastructure-as-code/what-is-terraform.md)                                                                                                                     | 🟢 Beginner     |
| 28  | [What is Ansible?](./infrastructure-as-code/what-is-ansible.md)                                                                                                                         | 🟢 Beginner     |
| 29  | [What is the difference between Ansible and Terraform?](./infrastructure-as-code/what-is-the-difference-between-ansible-and-terraform.md)                                               | 🟡 Intermediate |
| 30  | [What are Terraform providers?](./infrastructure-as-code/what-are-terraform-providers.md)                                                                                               | 🟡 Intermediate |
| 235 | [How do you import existing cloud infrastructure into Terraform?](./infrastructure-as-code/how-do-you-import-existing-cloud-infrastructure-into-terraform.md)                           | 🟡 Intermediate |
| 261 | [How do you manage Terraform state safely in a team?](./infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md)                                                   | 🟡 Intermediate |
| 262 | [How do you recover a lost or corrupted Terraform state file?](./infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md)                                 | 🔴 Advanced     |
| 421 | [What is immutable infrastructure and how do you adopt it?](./infrastructure-as-code/what-is-immutable-infrastructure-and-how-do-you-adopt-it.md)                                       | 🟡 Intermediate |
| 422 | [How do you structure Terraform code for multiple environments and providers?](./infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md) | 🔴 Advanced     |
| 462 | [What do terraform init, plan, apply, and refresh actually do?](./infrastructure-as-code/what-do-terraform-init-plan-apply-and-refresh-actually-do.md)                                  | 🟢 Beginner     |
| 463 | [How do you write and structure a reusable Terraform module?](./infrastructure-as-code/how-do-you-write-and-structure-a-reusable-terraform-module.md)                                   | 🟡 Intermediate |
| 464 | [What is the difference between count and for_each in Terraform?](./infrastructure-as-code/what-is-the-difference-between-count-and-for-each-in-terraform.md)                           | 🟡 Intermediate |
| 465 | [How do you stop Terraform from destroying or recreating a resource?](./infrastructure-as-code/how-do-you-stop-terraform-from-destroying-or-recreating-a-resource.md)                   | 🔴 Advanced     |
| 466 | [How do you run Terraform through a CI/CD pipeline?](./infrastructure-as-code/how-do-you-run-terraform-through-a-ci-cd-pipeline.md)                                                     | 🔴 Advanced     |
| 467 | [What are Terraform provisioners and when should you avoid them?](./infrastructure-as-code/what-are-terraform-provisioners-and-when-should-you-avoid-them.md)                           | 🟡 Intermediate |

</details>

<details>
<summary><b>Configuration Management</b> · 11 questions · 🟢 1 🟡 9 🔴 1</summary>

[Open the Configuration Management index →](./configuration-management/README.md)

| No. | Question                                                                                                                                                                          | Difficulty      |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 51  | [What is Configuration Management?](./configuration-management/what-is-configuration-management.md)                                                                               | 🟢 Beginner     |
| 52  | [What is Puppet?](./configuration-management/what-is-puppet.md)                                                                                                                   | 🟡 Intermediate |
| 53  | [What is Chef?](./configuration-management/what-is-chef.md)                                                                                                                       | 🟡 Intermediate |
| 54  | [What is Salt (SaltStack)?](./configuration-management/what-is-salt-saltstack.md)                                                                                                 | 🟡 Intermediate |
| 55  | [Compare different Configuration Management tools](./configuration-management/compare-different-configuration-management-tools.md)                                                | 🟡 Intermediate |
| 283 | [How do you run Ansible at scale across thousands of hosts?](./configuration-management/how-do-you-run-ansible-at-scale-across-thousands-of-hosts.md)                             | 🔴 Advanced     |
| 430 | [How do you patch hundreds of servers safely?](./configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)                                                         | 🟡 Intermediate |
| 468 | [How do you structure an Ansible role and share it through Galaxy?](./configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)               | 🟡 Intermediate |
| 469 | [How do you manage Ansible inventories and variables across environments?](./configuration-management/how-do-you-manage-ansible-inventories-and-variables-across-environments.md) | 🟡 Intermediate |
| 470 | [How do you handle secrets in Ansible with Vault?](./configuration-management/how-do-you-handle-secrets-in-ansible-with-vault.md)                                                 | 🟡 Intermediate |
| 471 | [How do you debug and safely test an Ansible playbook?](./configuration-management/how-do-you-debug-and-safely-test-an-ansible-playbook.md)                                       | 🟡 Intermediate |

</details>

<details>
<summary><b>DevOps Tools and Automation</b> · 9 questions · 🟢 2 🟡 6 🔴 1</summary>

[Open the DevOps Tools and Automation index →](./devops-tools-and-automation/README.md)

| No. | Question                                                                                                                                                       | Difficulty      |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 86  | [What is Infrastructure Automation?](./devops-tools-and-automation/what-is-infrastructure-automation.md)                                                       | 🟢 Beginner     |
| 87  | [What is GitOps?](./devops-tools-and-automation/what-is-gitops.md)                                                                                             | 🟡 Intermediate |
| 88  | [What is ArgoCD?](./devops-tools-and-automation/what-is-argocd.md)                                                                                             | 🟡 Intermediate |
| 89  | [What is Tekton?](./devops-tools-and-automation/what-is-tekton.md)                                                                                             | 🟡 Intermediate |
| 90  | [What are Deployment Strategies?](./devops-tools-and-automation/what-are-deployment-strategies.md)                                                             | 🟡 Intermediate |
| 289 | [How do you consolidate a sprawling DevOps toolchain?](./devops-tools-and-automation/how-do-you-consolidate-a-sprawling-devops-toolchain.md)                   | 🔴 Advanced     |
| 428 | [How do you troubleshoot a GitOps pipeline that will not sync?](./devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md) | 🟡 Intermediate |
| 460 | [How do you manage build artefacts with Nexus or Artifactory?](./devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)   | 🟡 Intermediate |
| 461 | [What do you need to know about Maven as a DevOps engineer?](./devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)       | 🟢 Beginner     |

</details>

### ☁️ Cloud Providers

_79 questions_

<details>
<summary><b>Cloud Platforms</b> · 7 questions · 🟢 5 🟡 1 🔴 1</summary>

[Open the Cloud Platforms index →](./cloud-platforms/README.md)

| No. | Question                                                                                                                             | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 21  | [What is Cloud Computing?](./cloud-platforms/what-is-cloud-computing.md)                                                             | 🟢 Beginner     |
| 22  | [What is AWS (Amazon Web Services)?](./cloud-platforms/what-is-aws-amazon-web-services.md)                                           | 🟢 Beginner     |
| 23  | [What is Azure?](./cloud-platforms/what-is-azure.md)                                                                                 | 🟢 Beginner     |
| 24  | [What is Google Cloud Platform (GCP)?](./cloud-platforms/what-is-google-cloud-platform-gcp.md)                                       | 🟢 Beginner     |
| 25  | [What are the different types of cloud services?](./cloud-platforms/what-are-the-different-types-of-cloud-services.md)               | 🟢 Beginner     |
| 281 | [How do you choose a cloud provider for a new workload?](./cloud-platforms/how-do-you-choose-a-cloud-provider-for-a-new-workload.md) | 🟡 Intermediate |
| 282 | [How does networking differ across AWS, Azure, and GCP?](./cloud-platforms/how-does-networking-differ-across-aws-azure-and-gcp.md)   | 🔴 Advanced     |

</details>

<details>
<summary><b>Cloud Cost Optimization</b> · 8 questions · 🟢 2 🟡 5 🔴 1</summary>

[Open the Cloud Cost Optimization index →](./cloud-cost-optimization/README.md)

| No. | Question                                                                                                                                                                                                   | Difficulty      |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 91  | [What is Cloud Cost Optimization?](./cloud-cost-optimization/what-is-cloud-cost-optimization.md)                                                                                                           | 🟢 Beginner     |
| 92  | [What are Reserved Instances?](./cloud-cost-optimization/what-are-reserved-instances.md)                                                                                                                   | 🟢 Beginner     |
| 93  | [What is Spot Instance pricing?](./cloud-cost-optimization/what-is-spot-instance-pricing.md)                                                                                                               | 🟡 Intermediate |
| 94  | [How to implement cost tagging strategy?](./cloud-cost-optimization/how-to-implement-cost-tagging-strategy.md)                                                                                             | 🟡 Intermediate |
| 95  | [What are cost allocation reports?](./cloud-cost-optimization/what-are-cost-allocation-reports.md)                                                                                                         | 🟡 Intermediate |
| 246 | [How do you implement real-time Kubernetes cost monitoring using OpenCost or Kubecost?](./cloud-cost-optimization/how-do-you-implement-real-time-kubernetes-cost-monitoring-using-opencost-or-kubecost.md) | 🟡 Intermediate |
| 278 | [How do you cut a cloud bill without hurting reliability?](./cloud-cost-optimization/how-do-you-cut-a-cloud-bill-without-hurting-reliability.md)                                                           | 🔴 Advanced     |
| 506 | [How do you investigate a sudden spike in your cloud bill?](./cloud-cost-optimization/how-do-you-investigate-a-sudden-spike-in-your-cloud-bill.md)                                                         | 🟡 Intermediate |

</details>

<details>
<summary><b>Cloud Migration</b> · 8 questions · 🟢 1 🟡 4 🔴 3</summary>

[Open the Cloud Migration index →](./cloud-migration/README.md)

| No. | Question                                                                                                                                                                             | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 136 | [What is Cloud Migration?](./cloud-migration/what-is-cloud-migration.md)                                                                                                             | 🟢 Beginner     |
| 137 | [What are Cloud Migration Strategies?](./cloud-migration/what-are-cloud-migration-strategies.md)                                                                                     | 🟡 Intermediate |
| 138 | [What is Cloud Assessment?](./cloud-migration/what-is-cloud-assessment.md)                                                                                                           | 🟡 Intermediate |
| 139 | [What is Application Modernization?](./cloud-migration/what-is-application-modernization.md)                                                                                         | 🟡 Intermediate |
| 140 | [What are Cloud Migration Tools?](./cloud-migration/what-are-cloud-migration-tools.md)                                                                                               | 🟡 Intermediate |
| 279 | [How do you migrate a production database to the cloud with near-zero downtime?](./cloud-migration/how-do-you-migrate-a-production-database-to-the-cloud-with-near-zero-downtime.md) | 🔴 Advanced     |
| 431 | [How do you containerise a legacy application and move it to Kubernetes?](./cloud-migration/how-do-you-containerise-a-legacy-application-and-move-it-to-kubernetes.md)               | 🔴 Advanced     |
| 432 | [How do you migrate a Kubernetes cluster to another cloud provider?](./cloud-migration/how-do-you-migrate-a-kubernetes-cluster-to-another-cloud-provider.md)                         | 🔴 Advanced     |

</details>

<details>
<summary><b>AWS Engineering</b> · 26 questions · 🟢 6 🟡 13 🔴 7</summary>

[Open the AWS Engineering index →](./aws-engineering/README.md)

| No. | Question                                                                                                                                                                                           | Difficulty      |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 191 | [How do you design a production-ready VPC on AWS?](./aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md)                                                                           | 🟡 Intermediate |
| 192 | [How does AWS IAM evaluate a request?](./aws-engineering/how-does-aws-iam-evaluate-a-request.md)                                                                                                   | 🔴 Advanced     |
| 193 | [What is the difference between ECS, EKS, and Fargate?](./aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)                                                                   | 🟡 Intermediate |
| 194 | [How do Auto Scaling groups and load balancers work together on AWS?](./aws-engineering/how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md)                                     | 🟡 Intermediate |
| 195 | [What are the S3 storage classes and when do you use each?](./aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md)                                                         | 🟡 Intermediate |
| 196 | [How do you run a highly available database on AWS?](./aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md)                                                                       | 🔴 Advanced     |
| 197 | [How do you structure a multi-account AWS organisation?](./aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md)                                                               | 🔴 Advanced     |
| 198 | [When do you choose CloudFormation, CDK, or Terraform on AWS?](./aws-engineering/when-do-you-choose-cloudformation-cdk-or-terraform-on-aws.md)                                                     | 🟡 Intermediate |
| 236 | [How do you automate EC2 log shipping to S3 with IAM boundaries and CloudWatch?](./aws-engineering/how-do-you-automate-ec2-log-shipping-to-s3-with-iam-boundaries-and-cloudwatch.md)               | 🟡 Intermediate |
| 247 | [How do you secure pod access to AWS resources using EKS Pod Identity or IRSA?](./aws-engineering/how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md)                 | 🟡 Intermediate |
| 248 | [How do you build a CI/CD pipeline using AWS CodePipeline, CodeBuild, and CodeDeploy?](./aws-engineering/how-do-you-build-a-ci-cd-pipeline-using-aws-codepipeline-codebuild-and-codedeploy.md)     | 🟡 Intermediate |
| 249 | [How do you architect an end-to-end production DevOps project on AWS?](./aws-engineering/how-do-you-architect-an-end-to-end-production-devops-project-on-aws.md)                                   | 🔴 Advanced     |
| 277 | [What are the core AWS services a DevOps engineer uses daily?](./aws-engineering/what-are-the-core-aws-services-a-devops-engineer-uses-daily.md)                                                   | 🟢 Beginner     |
| 472 | [What is the difference between a security group and a network ACL?](./aws-engineering/what-is-the-difference-between-a-security-group-and-a-network-acl.md)                                       | 🟢 Beginner     |
| 473 | [How does a private subnet reach the internet?](./aws-engineering/how-does-a-private-subnet-reach-the-internet.md)                                                                                 | 🟢 Beginner     |
| 474 | [What are VPC endpoints, and when do you use a gateway versus an interface endpoint?](./aws-engineering/what-are-vpc-endpoints-and-when-do-you-use-a-gateway-versus-an-interface-endpoint.md)      | 🟡 Intermediate |
| 475 | [How do you connect many VPCs — peering, Transit Gateway, or PrivateLink?](./aws-engineering/how-do-you-connect-many-vpcs-peering-transit-gateway-or-privatelink.md)                               | 🔴 Advanced     |
| 476 | [How do you access an instance in a private subnet without SSH keys or a bastion host?](./aws-engineering/how-do-you-access-an-instance-in-a-private-subnet-without-ssh-keys-or-a-bastion-host.md) | 🟡 Intermediate |
| 477 | [How do you authenticate to AWS without long-lived access keys?](./aws-engineering/how-do-you-authenticate-to-aws-without-long-lived-access-keys.md)                                               | 🔴 Advanced     |
| 478 | [How do you secure and manage the lifecycle of an S3 bucket?](./aws-engineering/how-do-you-secure-and-manage-the-lifecycle-of-an-s3-bucket.md)                                                     | 🟡 Intermediate |
| 479 | [How do you choose between EBS, EFS, and S3?](./aws-engineering/how-do-you-choose-between-ebs-efs-and-s3.md)                                                                                       | 🟢 Beginner     |
| 480 | [How do you upgrade, scale, and resize an RDS instance without downtime?](./aws-engineering/how-do-you-upgrade-scale-and-resize-an-rds-instance-without-downtime.md)                               | 🔴 Advanced     |
| 481 | [What are the DNS record types, and how do you delegate a domain?](./aws-engineering/what-are-the-dns-record-types-and-how-do-you-delegate-a-domain.md)                                            | 🟢 Beginner     |
| 482 | [How do you configure Auto Scaling group policies, health checks, and instance refresh?](./aws-engineering/how-do-you-configure-auto-scaling-group-policies-health-checks-and-instance-refresh.md) | 🟡 Intermediate |
| 483 | [What is the difference between CloudWatch, CloudTrail, and AWS Config?](./aws-engineering/what-is-the-difference-between-cloudwatch-cloudtrail-and-aws-config.md)                                 | 🟢 Beginner     |
| 484 | [How do you run a service on Amazon ECS?](./aws-engineering/how-do-you-run-a-service-on-amazon-ecs.md)                                                                                             | 🟡 Intermediate |

</details>

<details>
<summary><b>Azure Engineering</b> · 13 questions · 🟢 1 🟡 10 🔴 2</summary>

[Open the Azure Engineering index →](./azure-engineering/README.md)

| No. | Question                                                                                                                                                                                                                 | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 199 | [How is the Azure resource hierarchy organised?](./azure-engineering/how-is-the-azure-resource-hierarchy-organised.md)                                                                                                   | 🟢 Beginner     |
| 200 | [What is Microsoft Entra ID and how does Azure RBAC work?](./azure-engineering/what-is-microsoft-entra-id-and-how-does-azure-rbac-work.md)                                                                               | 🟡 Intermediate |
| 201 | [How do you design an Azure virtual network?](./azure-engineering/how-do-you-design-an-azure-virtual-network.md)                                                                                                         | 🟡 Intermediate |
| 202 | [What is Azure Kubernetes Service (AKS)?](./azure-engineering/what-is-azure-kubernetes-service-aks.md)                                                                                                                   | 🟡 Intermediate |
| 203 | [What is Bicep and how does it compare to ARM templates?](./azure-engineering/what-is-bicep-and-how-does-it-compare-to-arm-templates.md)                                                                                 | 🟡 Intermediate |
| 204 | [What is Azure Policy and how do landing zones use it?](./azure-engineering/what-is-azure-policy-and-how-do-landing-zones-use-it.md)                                                                                     | 🔴 Advanced     |
| 205 | [How do you monitor Azure with Azure Monitor and KQL?](./azure-engineering/how-do-you-monitor-azure-with-azure-monitor-and-kql.md)                                                                                       | 🟡 Intermediate |
| 206 | [When do you choose App Service, Container Apps, or Azure Functions?](./azure-engineering/when-do-you-choose-app-service-container-apps-or-azure-functions.md)                                                           | 🟡 Intermediate |
| 250 | [How do you architect an end-to-end production DevOps project on Azure?](./azure-engineering/how-do-you-architect-an-end-to-end-production-devops-project-on-azure.md)                                                   | 🔴 Advanced     |
| 485 | [How do you build a CI/CD pipeline in Azure DevOps?](./azure-engineering/how-do-you-build-a-ci-cd-pipeline-in-azure-devops.md)                                                                                           | 🟡 Intermediate |
| 486 | [How do you consume Azure Key Vault secrets from AKS and Azure Pipelines?](./azure-engineering/how-do-you-consume-azure-key-vault-secrets-from-aks-and-azure-pipelines.md)                                               | 🟡 Intermediate |
| 487 | [How do you choose between Azure Load Balancer, Application Gateway, and Front Door?](./azure-engineering/how-do-you-choose-between-azure-load-balancer-application-gateway-and-front-door.md)                           | 🟡 Intermediate |
| 488 | [What is the difference between a managed identity, a service principal, and an app registration?](./azure-engineering/what-is-the-difference-between-a-managed-identity-a-service-principal-and-an-app-registration.md) | 🟡 Intermediate |

</details>

<details>
<summary><b>GCP Engineering</b> · 9 questions · 🟢 1 🟡 7 🔴 1</summary>

[Open the GCP Engineering index →](./gcp-engineering/README.md)

| No. | Question                                                                                                                                                         | Difficulty      |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 207 | [How is the GCP resource hierarchy organised?](./gcp-engineering/how-is-the-gcp-resource-hierarchy-organised.md)                                                 | 🟢 Beginner     |
| 208 | [How does IAM work in Google Cloud?](./gcp-engineering/how-does-iam-work-in-google-cloud.md)                                                                     | 🟡 Intermediate |
| 209 | [What makes a Google Cloud VPC different?](./gcp-engineering/what-makes-a-google-cloud-vpc-different.md)                                                         | 🟡 Intermediate |
| 210 | [What is the difference between GKE Standard and GKE Autopilot?](./gcp-engineering/what-is-the-difference-between-gke-standard-and-gke-autopilot.md)             | 🟡 Intermediate |
| 211 | [What is Cloud Run and when do you choose it?](./gcp-engineering/what-is-cloud-run-and-when-do-you-choose-it.md)                                                 | 🟡 Intermediate |
| 212 | [How do you monitor Google Cloud with the Cloud Operations Suite?](./gcp-engineering/how-do-you-monitor-google-cloud-with-the-cloud-operations-suite.md)         | 🟡 Intermediate |
| 213 | [How do you manage Google Cloud infrastructure as code?](./gcp-engineering/how-do-you-manage-google-cloud-infrastructure-as-code.md)                             | 🟡 Intermediate |
| 214 | [When do you use BigQuery, Cloud SQL, or Spanner?](./gcp-engineering/when-do-you-use-bigquery-cloud-sql-or-spanner.md)                                           | 🟡 Intermediate |
| 251 | [How do you architect an end-to-end production DevOps project on GCP?](./gcp-engineering/how-do-you-architect-an-end-to-end-production-devops-project-on-gcp.md) | 🔴 Advanced     |

</details>

<details>
<summary><b>Cloud Engineering</b> · 8 questions · 🟢 1 🟡 4 🔴 3</summary>

[Open the Cloud Engineering index →](./cloud-engineering/README.md)

| No. | Question                                                                                                                                                     | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 215 | [What is a cloud landing zone?](./cloud-engineering/what-is-a-cloud-landing-zone.md)                                                                         | 🟡 Intermediate |
| 216 | [How do you connect an on-premises network to the cloud?](./cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md)                     | 🟡 Intermediate |
| 217 | [How do you design least-privilege identity in the cloud?](./cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md)                   | 🔴 Advanced     |
| 218 | [How do you design for multi-region resilience?](./cloud-engineering/how-do-you-design-for-multi-region-resilience.md)                                       | 🔴 Advanced     |
| 219 | [What are the real trade-offs of multi-cloud?](./cloud-engineering/what-are-the-real-trade-offs-of-multi-cloud.md)                                           | 🔴 Advanced     |
| 220 | [How do you manage DNS and global traffic routing?](./cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md)                                 | 🟡 Intermediate |
| 221 | [How do the core services of AWS, Azure, and GCP map to each other?](./cloud-engineering/how-do-the-core-services-of-aws-azure-and-gcp-map-to-each-other.md) | 🟢 Beginner     |
| 435 | [How do you troubleshoot a DNS problem in production?](./cloud-engineering/how-do-you-troubleshoot-a-dns-problem-in-production.md)                           | 🟡 Intermediate |

</details>

### 🏗️ Architecture and Scale

_47 questions_

<details>
<summary><b>Scalability and High Availability</b> · 9 questions · 🟢 4 🟡 2 🔴 3</summary>

[Open the Scalability and High Availability index →](./scalability-and-high-availability/README.md)

| No. | Question                                                                                                                                                                                                                     | Difficulty      |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 56  | [What is Scalability in DevOps?](./scalability-and-high-availability/what-is-scalability-in-devops.md)                                                                                                                       | 🟢 Beginner     |
| 57  | [What is High Availability?](./scalability-and-high-availability/what-is-high-availability.md)                                                                                                                               | 🟢 Beginner     |
| 58  | [What is Load Balancing?](./scalability-and-high-availability/what-is-load-balancing.md)                                                                                                                                     | 🟢 Beginner     |
| 59  | [What is Auto Scaling?](./scalability-and-high-availability/what-is-auto-scaling.md)                                                                                                                                         | 🟢 Beginner     |
| 60  | [What is Disaster Recovery?](./scalability-and-high-availability/what-is-disaster-recovery.md)                                                                                                                               | 🟡 Intermediate |
| 269 | [What is the difference between a layer 4 and a layer 7 load balancer?](./scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md)                                         | 🟡 Intermediate |
| 300 | [How do you design a system to degrade gracefully under overload?](./scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md)                                                   | 🔴 Advanced     |
| 419 | [How do you troubleshoot a load balancer returning 5xx errors or sending traffic unevenly?](./scalability-and-high-availability/how-do-you-troubleshoot-a-load-balancer-returning-5xx-errors-or-sending-traffic-unevenly.md) | 🔴 Advanced     |
| 420 | [Why did your autoscaling not kick in during a traffic spike?](./scalability-and-high-availability/why-did-your-autoscaling-not-kick-in-during-a-traffic-spike.md)                                                           | 🔴 Advanced     |

</details>

<details>
<summary><b>Cloud Native Architecture</b> · 8 questions · 🟢 1 🟡 4 🔴 3</summary>

[Open the Cloud Native Architecture index →](./cloud-native-architecture/README.md)

| No. | Question                                                                                                                                                                     | Difficulty      |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 66  | [What is Cloud Native Architecture?](./cloud-native-architecture/what-is-cloud-native-architecture.md)                                                                       | 🟡 Intermediate |
| 67  | [What are Microservices?](./cloud-native-architecture/what-are-microservices.md)                                                                                             | 🟡 Intermediate |
| 68  | [What is Service Mesh?](./cloud-native-architecture/what-is-service-mesh.md)                                                                                                 | 🔴 Advanced     |
| 69  | [What is Event-Driven Architecture?](./cloud-native-architecture/what-is-event-driven-architecture.md)                                                                       | 🟡 Intermediate |
| 70  | [What are the 12-Factor App principles?](./cloud-native-architecture/what-are-the-12-factor-app-principles.md)                                                               | 🟡 Intermediate |
| 280 | [What is the difference between a monolith and microservices?](./cloud-native-architecture/what-is-the-difference-between-a-monolith-and-microservices.md)                   | 🟢 Beginner     |
| 426 | [How do you troubleshoot high latency in a microservices architecture?](./cloud-native-architecture/how-do-you-troubleshoot-high-latency-in-a-microservices-architecture.md) | 🔴 Advanced     |
| 505 | [How do you design a secure, highly available three-tier architecture?](./cloud-native-architecture/how-do-you-design-a-secure-highly-available-three-tier-architecture.md)  | 🔴 Advanced     |

</details>

<details>
<summary><b>Performance Testing</b> · 6 questions · 🟢 3 🟡 2 🔴 1</summary>

[Open the Performance Testing index →](./performance-testing/README.md)

| No. | Question                                                                                                                   | Difficulty      |
| --- | -------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 71  | [What is Performance Testing?](./performance-testing/what-is-performance-testing.md)                                       | 🟢 Beginner     |
| 72  | [What are different types of Performance Tests?](./performance-testing/what-are-different-types-of-performance-tests.md)   | 🟢 Beginner     |
| 73  | [What are Performance Testing Tools?](./performance-testing/what-are-performance-testing-tools.md)                         | 🟢 Beginner     |
| 74  | [What are Performance Testing Best Practices?](./performance-testing/what-are-performance-testing-best-practices.md)       | 🟡 Intermediate |
| 75  | [How to analyze Performance Test Results?](./performance-testing/how-to-analyze-performance-test-results.md)               | 🟡 Intermediate |
| 298 | [How do you load test safely against production?](./performance-testing/how-do-you-load-test-safely-against-production.md) | 🔴 Advanced     |

</details>

<details>
<summary><b>API Gateway and Service Mesh</b> · 8 questions · 🟢 3 🟡 3 🔴 2</summary>

[Open the API Gateway and Service Mesh index →](./api-gateway-and-service-mesh/README.md)

| No. | Question                                                                                                                                                                                                 | Difficulty      |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 76  | [What is an API Gateway?](./api-gateway-and-service-mesh/what-is-an-api-gateway.md)                                                                                                                      | 🟡 Intermediate |
| 77  | [What are the benefits of using API Gateway?](./api-gateway-and-service-mesh/what-are-the-benefits-of-using-api-gateway.md)                                                                              | 🟢 Beginner     |
| 78  | [What is API Security?](./api-gateway-and-service-mesh/what-is-api-security.md)                                                                                                                          | 🟡 Intermediate |
| 79  | [What is Rate Limiting?](./api-gateway-and-service-mesh/what-is-rate-limiting.md)                                                                                                                        | 🟢 Beginner     |
| 80  | [What is API Documentation?](./api-gateway-and-service-mesh/what-is-api-documentation.md)                                                                                                                | 🟢 Beginner     |
| 276 | [How do you run a service mesh in production without the sidecar tax?](./api-gateway-and-service-mesh/how-do-you-run-a-service-mesh-in-production-without-the-sidecar-tax.md)                            | 🔴 Advanced     |
| 427 | [How do you debug a service mesh that is breaking service-to-service traffic?](./api-gateway-and-service-mesh/how-do-you-debug-a-service-mesh-that-is-breaking-service-to-service-traffic.md)            | 🔴 Advanced     |
| 507 | [What do the common HTTP status codes mean, and how do you debug a 502, 503, or 504?](./api-gateway-and-service-mesh/what-do-the-common-http-status-codes-mean-and-how-do-you-debug-a-502-503-or-504.md) | 🟡 Intermediate |

</details>

<details>
<summary><b>Serverless Architecture</b> · 8 questions · 🟢 4 🟡 3 🔴 1</summary>

[Open the Serverless Architecture index →](./serverless-architecture/README.md)

| No. | Question                                                                                                                                                       | Difficulty      |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 106 | [What is Serverless Computing?](./serverless-architecture/what-is-serverless-computing.md)                                                                     | 🟢 Beginner     |
| 107 | [What is AWS Lambda?](./serverless-architecture/what-is-aws-lambda.md)                                                                                         | 🟢 Beginner     |
| 108 | [What are the benefits of Serverless?](./serverless-architecture/what-are-the-benefits-of-serverless.md)                                                       | 🟢 Beginner     |
| 109 | [What are Serverless Best Practices?](./serverless-architecture/what-are-serverless-best-practices.md)                                                         | 🟡 Intermediate |
| 110 | [What is Function as a Service (FaaS)?](./serverless-architecture/what-is-function-as-a-service-faas.md)                                                       | 🟢 Beginner     |
| 303 | [How do you design a serverless system for production?](./serverless-architecture/how-do-you-design-a-serverless-system-for-production.md)                     | 🔴 Advanced     |
| 423 | [How do you monitor and debug a serverless application?](./serverless-architecture/how-do-you-monitor-and-debug-a-serverless-application.md)                   | 🟡 Intermediate |
| 424 | [How do you build a CI/CD pipeline for a serverless application?](./serverless-architecture/how-do-you-build-a-ci-cd-pipeline-for-a-serverless-application.md) | 🟡 Intermediate |

</details>

<details>
<summary><b>Database Management in DevOps</b> · 8 questions · 🟢 1 🟡 4 🔴 3</summary>

[Open the Database Management in DevOps index →](./database-management-in-devops/README.md)

| No. | Question                                                                                                                                                                                 | Difficulty      |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 111 | [What is Database DevOps?](./database-management-in-devops/what-is-database-devops.md)                                                                                                   | 🟡 Intermediate |
| 112 | [What is Database Version Control?](./database-management-in-devops/what-is-database-version-control.md)                                                                                 | 🟡 Intermediate |
| 113 | [What are Database Migration Tools?](./database-management-in-devops/what-are-database-migration-tools.md)                                                                               | 🟡 Intermediate |
| 114 | [What is Database Backup Strategy?](./database-management-in-devops/what-is-database-backup-strategy.md)                                                                                 | 🟡 Intermediate |
| 115 | [What is Database Performance Tuning?](./database-management-in-devops/what-is-database-performance-tuning.md)                                                                           | 🔴 Advanced     |
| 286 | [What does a DevOps engineer need to know about databases?](./database-management-in-devops/what-does-a-devops-engineer-need-to-know-about-databases.md)                                 | 🟢 Beginner     |
| 417 | [How do you troubleshoot a database that is slow or timing out under load?](./database-management-in-devops/how-do-you-troubleshoot-a-database-that-is-slow-or-timing-out-under-load.md) | 🔴 Advanced     |
| 418 | [How do you change a production database schema without downtime?](./database-management-in-devops/how-do-you-change-a-production-database-schema-without-downtime.md)                   | 🔴 Advanced     |

</details>

### 📈 Reliability and Operations

_60 questions_

<details>
<summary><b>Monitoring and Logging</b> · 9 questions · 🟢 4 🟡 4 🔴 1</summary>

[Open the Monitoring and Logging index →](./monitoring-and-logging/README.md)

| No. | Question                                                                                                                                                                     | Difficulty      |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 31  | [What is monitoring in DevOps?](./monitoring-and-logging/what-is-monitoring-in-devops.md)                                                                                    | 🟢 Beginner     |
| 32  | [What is ELK Stack?](./monitoring-and-logging/what-is-elk-stack.md)                                                                                                          | 🟡 Intermediate |
| 33  | [What is Prometheus?](./monitoring-and-logging/what-is-prometheus.md)                                                                                                        | 🟢 Beginner     |
| 34  | [What is Grafana?](./monitoring-and-logging/what-is-grafana.md)                                                                                                              | 🟢 Beginner     |
| 35  | [Explain the difference between monitoring and logging](./monitoring-and-logging/explain-the-difference-between-monitoring-and-logging.md)                                   | 🟢 Beginner     |
| 253 | [How do you write effective PromQL queries and Alertmanager rules?](./monitoring-and-logging/how-do-you-write-effective-promql-queries-and-alertmanager-rules.md)            | 🟡 Intermediate |
| 296 | [How do you design a logging pipeline that stays affordable at scale?](./monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md)      | 🔴 Advanced     |
| 500 | [How does Prometheus collect metrics, and what components sit around it?](./monitoring-and-logging/how-does-prometheus-collect-metrics-and-what-components-sit-around-it.md) | 🟡 Intermediate |
| 501 | [How do the ELK and EFK stacks fit together?](./monitoring-and-logging/how-do-the-elk-and-efk-stacks-fit-together.md)                                                        | 🟡 Intermediate |

</details>

<details>
<summary><b>Backup and Disaster Recovery</b> · 7 questions · 🟢 4 🟡 2 🔴 1</summary>

[Open the Backup and Disaster Recovery index →](./backup-and-disaster-recovery/README.md)

| No. | Question                                                                                                                                                                                | Difficulty      |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 61  | [What is Backup and Disaster Recovery?](./backup-and-disaster-recovery/what-is-backup-and-disaster-recovery.md)                                                                         | 🟢 Beginner     |
| 62  | [What are different types of backups?](./backup-and-disaster-recovery/what-are-different-types-of-backups.md)                                                                           | 🟢 Beginner     |
| 63  | [What is RPO and RTO?](./backup-and-disaster-recovery/what-is-rpo-and-rto.md)                                                                                                           | 🟢 Beginner     |
| 64  | [What is Business Continuity Planning?](./backup-and-disaster-recovery/what-is-business-continuity-planning.md)                                                                         | 🟡 Intermediate |
| 65  | [What are backup best practices?](./backup-and-disaster-recovery/what-are-backup-best-practices.md)                                                                                     | 🟢 Beginner     |
| 239 | [How do you execute a Disaster Recovery failover with minimal RTO and RPO?](./backup-and-disaster-recovery/how-do-you-execute-a-disaster-recovery-failover-with-minimal-rto-and-rpo.md) | 🔴 Advanced     |
| 436 | [How do you verify that your backups can actually be restored?](./backup-and-disaster-recovery/how-do-you-verify-that-your-backups-can-actually-be-restored.md)                         | 🟡 Intermediate |

</details>

<details>
<summary><b>Site Reliability Engineering (SRE)</b> · 9 questions · 🟢 1 🟡 6 🔴 2</summary>

[Open the Site Reliability Engineering (SRE) index →](./site-reliability-engineering/README.md)

| No. | Question                                                                                                                                                                      | Difficulty      |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 96  | [What is Site Reliability Engineering?](./site-reliability-engineering/what-is-site-reliability-engineering.md)                                                               | 🟢 Beginner     |
| 97  | [What are Service Level Objectives (SLOs)?](./site-reliability-engineering/what-are-service-level-objectives-slos.md)                                                         | 🟡 Intermediate |
| 98  | [What are Service Level Indicators (SLIs)?](./site-reliability-engineering/what-are-service-level-indicators-slis.md)                                                         | 🟡 Intermediate |
| 99  | [What is Error Budget?](./site-reliability-engineering/what-is-error-budget.md)                                                                                               | 🟡 Intermediate |
| 100 | [What is Toil in SRE?](./site-reliability-engineering/what-is-toil-in-sre.md)                                                                                                 | 🟡 Intermediate |
| 230 | [How do you do capacity planning?](./site-reliability-engineering/how-do-you-do-capacity-planning.md)                                                                         | 🔴 Advanced     |
| 231 | [What is a production readiness review?](./site-reliability-engineering/what-is-a-production-readiness-review.md)                                                             | 🟡 Intermediate |
| 232 | [What is the difference between SRE, DevOps, and Platform Engineering?](./site-reliability-engineering/what-is-the-difference-between-sre-devops-and-platform-engineering.md) | 🟡 Intermediate |
| 233 | [How do you design alerts that page a human?](./site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md)                                                   | 🔴 Advanced     |

</details>

<details>
<summary><b>DevOps Metrics and KPIs</b> · 6 questions · 🟢 3 🟡 2 🔴 1</summary>

[Open the DevOps Metrics and KPIs index →](./devops-metrics-and-kpis/README.md)

| No. | Question                                                                                                                                                                 | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 101 | [What are DevOps Metrics?](./devops-metrics-and-kpis/what-are-devops-metrics.md)                                                                                         | 🟢 Beginner     |
| 102 | [What is Mean Time to Recovery (MTTR)?](./devops-metrics-and-kpis/what-is-mean-time-to-recovery-mttr.md)                                                                 | 🟢 Beginner     |
| 103 | [What is Change Failure Rate?](./devops-metrics-and-kpis/what-is-change-failure-rate.md)                                                                                 | 🟡 Intermediate |
| 104 | [What is Deployment Frequency?](./devops-metrics-and-kpis/what-is-deployment-frequency.md)                                                                               | 🟢 Beginner     |
| 105 | [What is Lead Time for Changes?](./devops-metrics-and-kpis/what-is-lead-time-for-changes.md)                                                                             | 🟡 Intermediate |
| 288 | [How do you build a metrics program without teams gaming the numbers?](./devops-metrics-and-kpis/how-do-you-build-a-metrics-program-without-teams-gaming-the-numbers.md) | 🔴 Advanced     |

</details>

<details>
<summary><b>Incident Management</b> · 7 questions · 🟢 2 🟡 3 🔴 2</summary>

[Open the Incident Management index →](./incident-management/README.md)

| No. | Question                                                                                                                                   | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 121 | [What is Incident Management?](./incident-management/what-is-incident-management.md)                                                       | 🟢 Beginner     |
| 122 | [What is an Incident Response Plan?](./incident-management/what-is-an-incident-response-plan.md)                                           | 🟡 Intermediate |
| 123 | [What is Post-Mortem Analysis?](./incident-management/what-is-post-mortem-analysis.md)                                                     | 🟡 Intermediate |
| 124 | [What are Incident Severity Levels?](./incident-management/what-are-incident-severity-levels.md)                                           | 🟢 Beginner     |
| 125 | [What is On-Call Management?](./incident-management/what-is-on-call-management.md)                                                         | 🟡 Intermediate |
| 292 | [How do you run a major incident as incident commander?](./incident-management/how-do-you-run-a-major-incident-as-incident-commander.md)   | 🔴 Advanced     |
| 425 | [How do you respond when a deployment breaks production?](./incident-management/how-do-you-respond-when-a-deployment-breaks-production.md) | 🔴 Advanced     |

</details>

<details>
<summary><b>Infrastructure Monitoring</b> · 7 questions · 🟢 2 🟡 4 🔴 1</summary>

[Open the Infrastructure Monitoring index →](./infrastructure-monitoring/README.md)

| No. | Question                                                                                                                                                                 | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 131 | [What is Infrastructure Monitoring?](./infrastructure-monitoring/what-is-infrastructure-monitoring.md)                                                                   | 🟢 Beginner     |
| 132 | [What are Monitoring Tools?](./infrastructure-monitoring/what-are-monitoring-tools.md)                                                                                   | 🟢 Beginner     |
| 133 | [What are Monitoring Best Practices?](./infrastructure-monitoring/what-are-monitoring-best-practices.md)                                                                 | 🟡 Intermediate |
| 134 | [What is Application Performance Monitoring?](./infrastructure-monitoring/what-is-application-performance-monitoring.md)                                                 | 🟡 Intermediate |
| 135 | [What is Log Management?](./infrastructure-monitoring/what-is-log-management.md)                                                                                         | 🟡 Intermediate |
| 293 | [How do you control metric cardinality and monitoring cost at scale?](./infrastructure-monitoring/how-do-you-control-metric-cardinality-and-monitoring-cost-at-scale.md) | 🔴 Advanced     |
| 433 | [How do you add monitoring to an application that has none?](./infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)                   | 🟡 Intermediate |

</details>

<details>
<summary><b>SLO Engineering</b> · 8 questions · 🟢 1 🟡 3 🔴 4</summary>

[Open the SLO Engineering index →](./slo-engineering/README.md)

| No. | Question                                                                                                                                         | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 177 | [How do you choose an SLO target?](./slo-engineering/how-do-you-choose-an-slo-target.md)                                                         | 🟡 Intermediate |
| 178 | [What is multi-window multi-burn-rate alerting?](./slo-engineering/what-is-multi-window-multi-burn-rate-alerting.md)                             | 🔴 Advanced     |
| 179 | [How do you measure a latency SLI correctly?](./slo-engineering/how-do-you-measure-a-latency-sli-correctly.md)                                   | 🔴 Advanced     |
| 180 | [What is an error budget policy?](./slo-engineering/what-is-an-error-budget-policy.md)                                                           | 🟡 Intermediate |
| 181 | [How do you define SLOs for batch and asynchronous workloads?](./slo-engineering/how-do-you-define-slos-for-batch-and-asynchronous-workloads.md) | 🔴 Advanced     |
| 182 | [How do you handle SLOs for dependencies you do not own?](./slo-engineering/how-do-you-handle-slos-for-dependencies-you-do-not-own.md)           | 🔴 Advanced     |
| 183 | [What tooling do you use to implement SLOs?](./slo-engineering/what-tooling-do-you-use-to-implement-slos.md)                                     | 🟡 Intermediate |
| 304 | [What do you need before you can set your first SLO?](./slo-engineering/what-do-you-need-before-you-can-set-your-first-slo.md)                   | 🟢 Beginner     |

</details>

<details>
<summary><b>SLA Management</b> · 7 questions · 🟢 2 🟡 4 🔴 1</summary>

[Open the SLA Management index →](./sla-management/README.md)

| No. | Question                                                                                                                                                  | Difficulty      |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 184 | [What is the difference between an SLA, an SLO, an SLI, and an OLA?](./sla-management/what-is-the-difference-between-an-sla-an-slo-an-sli-and-an-ola.md)  | 🟢 Beginner     |
| 185 | [How do you calculate allowed downtime for an availability target?](./sla-management/how-do-you-calculate-allowed-downtime-for-an-availability-target.md) | 🟢 Beginner     |
| 186 | [How do you calculate composite availability across dependencies?](./sla-management/how-do-you-calculate-composite-availability-across-dependencies.md)   | 🔴 Advanced     |
| 187 | [What belongs in a well-written SLA?](./sla-management/what-belongs-in-a-well-written-sla.md)                                                             | 🟡 Intermediate |
| 188 | [How do service credits work?](./sla-management/how-do-service-credits-work.md)                                                                           | 🟡 Intermediate |
| 189 | [How do you report SLA compliance to customers?](./sla-management/how-do-you-report-sla-compliance-to-customers.md)                                       | 🟡 Intermediate |
| 190 | [What do you do when you breach an SLA?](./sla-management/what-do-you-do-when-you-breach-an-sla.md)                                                       | 🟡 Intermediate |

</details>

### 🔐 Security

_38 questions_

<details>
<summary><b>Security and Compliance</b> · 6 questions · 🟢 1 🟡 3 🔴 2</summary>

[Open the Security and Compliance index →](./security-and-compliance/README.md)

| No. | Question                                                                                                                                                                          | Difficulty      |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 36  | [What is DevSecOps?](./security-and-compliance/what-is-devsecops.md)                                                                                                              | 🟢 Beginner     |
| 37  | [What is Infrastructure Security?](./security-and-compliance/what-is-infrastructure-security.md)                                                                                  | 🟡 Intermediate |
| 38  | [What is Container Security?](./security-and-compliance/what-is-container-security.md)                                                                                            | 🟡 Intermediate |
| 39  | [What is Compliance as Code?](./security-and-compliance/what-is-compliance-as-code.md)                                                                                            | 🔴 Advanced     |
| 40  | [What are Security Best Practices in DevOps?](./security-and-compliance/what-are-security-best-practices-in-devops.md)                                                            | 🟡 Intermediate |
| 434 | [How do you automate compliance checks for PCI DSS, SOC 2, HIPAA, and GDPR?](./security-and-compliance/how-do-you-automate-compliance-checks-for-pci-dss-soc-2-hipaa-and-gdpr.md) | 🔴 Advanced     |

</details>

<details>
<summary><b>Network Security</b> · 12 questions · 🟢 4 🟡 6 🔴 2</summary>

[Open the Network Security index →](./network-security/README.md)

| No. | Question                                                                                                                                                                              | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 116 | [What is Network Security in DevOps?](./network-security/what-is-network-security-in-devops.md)                                                                                       | 🟡 Intermediate |
| 117 | [What is Zero Trust Security?](./network-security/what-is-zero-trust-security.md)                                                                                                     | 🟡 Intermediate |
| 118 | [What is SSL/TLS?](./network-security/what-is-ssl-tls.md)                                                                                                                             | 🟢 Beginner     |
| 119 | [What is a Web Application Firewall (WAF)?](./network-security/what-is-a-web-application-firewall-waf.md)                                                                             | 🟢 Beginner     |
| 120 | [What is Network Segmentation?](./network-security/what-is-network-segmentation.md)                                                                                                   | 🟡 Intermediate |
| 270 | [What happens when a user opens your application in a browser?](./network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md)                                   | 🟡 Intermediate |
| 297 | [How do you design defence in depth for a cloud network?](./network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md)                                               | 🔴 Advanced     |
| 489 | [What is the OSI model, and what is the difference between TCP and UDP?](./network-security/what-is-the-osi-model-and-what-is-the-difference-between-tcp-and-udp.md)                  | 🟢 Beginner     |
| 490 | [How do you plan CIDR ranges and subnets?](./network-security/how-do-you-plan-cidr-ranges-and-subnets.md)                                                                             | 🟡 Intermediate |
| 491 | [How do you manage TLS certificates in production?](./network-security/how-do-you-manage-tls-certificates-in-production.md)                                                           | 🟡 Intermediate |
| 492 | [How do you protect a public web application against the OWASP Top 10 and DDoS?](./network-security/how-do-you-protect-a-public-web-application-against-the-owasp-top-10-and-ddos.md) | 🔴 Advanced     |
| 493 | [What is the difference between a reverse proxy and a forward proxy?](./network-security/what-is-the-difference-between-a-reverse-proxy-and-a-forward-proxy.md)                       | 🟢 Beginner     |

</details>

<details>
<summary><b>DevSecOps</b> · 12 questions · 🟢 1 🟡 7 🔴 4</summary>

[Open the DevSecOps index →](./devsecops/README.md)

| No. | Question                                                                                                                                                                         | Difficulty      |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 161 | [What does a DevSecOps pipeline look like end to end?](./devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)                                                       | 🟡 Intermediate |
| 162 | [What is the difference between SAST, DAST, IAST, and SCA?](./devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md)                                                | 🟡 Intermediate |
| 163 | [What is a Software Bill of Materials (SBOM)?](./devsecops/what-is-a-software-bill-of-materials-sbom.md)                                                                         | 🟡 Intermediate |
| 164 | [What is SLSA and how do you secure the software supply chain?](./devsecops/what-is-slsa-and-how-do-you-secure-the-software-supply-chain.md)                                     | 🔴 Advanced     |
| 165 | [How do you sign and verify container images?](./devsecops/how-do-you-sign-and-verify-container-images.md)                                                                       | 🟡 Intermediate |
| 166 | [How do you manage secrets in CI/CD pipelines?](./devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md)                                                                     | 🟡 Intermediate |
| 167 | [How do you scan Infrastructure as Code before it is applied?](./devsecops/how-do-you-scan-infrastructure-as-code-before-it-is-applied.md)                                       | 🟡 Intermediate |
| 168 | [How do you prioritise vulnerabilities without blocking delivery?](./devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md)                               | 🔴 Advanced     |
| 244 | [How do you enforce Kubernetes admission control with Kyverno or OPA Gatekeeper?](./devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md) | 🟡 Intermediate |
| 290 | [What does shift left security mean?](./devsecops/what-does-shift-left-security-mean.md)                                                                                         | 🟢 Beginner     |
| 429 | [How do you rotate secrets without downtime?](./devsecops/how-do-you-rotate-secrets-without-downtime.md)                                                                         | 🔴 Advanced     |
| 504 | [How do you manage Kubernetes secrets in a GitOps workflow?](./devsecops/how-do-you-manage-kubernetes-secrets-in-a-gitops-workflow.md)                                           | 🔴 Advanced     |

</details>

<details>
<summary><b>SecOps and Threat Detection</b> · 8 questions · 🟢 2 🟡 4 🔴 2</summary>

[Open the SecOps and Threat Detection index →](./secops/README.md)

| No. | Question                                                                                                            | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------- | --------------- |
| 169 | [What does a Security Operations Center (SOC) do?](./secops/what-does-a-security-operations-center-soc-do.md)       | 🟢 Beginner     |
| 170 | [What is a SIEM and how do you make one useful?](./secops/what-is-a-siem-and-how-do-you-make-one-useful.md)         | 🟡 Intermediate |
| 171 | [What is detection engineering?](./secops/what-is-detection-engineering.md)                                         | 🔴 Advanced     |
| 172 | [What is the MITRE ATT&CK framework?](./secops/what-is-the-mitre-att-and-ck-framework.md)                           | 🟡 Intermediate |
| 173 | [What is threat hunting?](./secops/what-is-threat-hunting.md)                                                       | 🔴 Advanced     |
| 174 | [How do you run a security incident response?](./secops/how-do-you-run-a-security-incident-response.md)             | 🟡 Intermediate |
| 175 | [What is EDR and how does it differ from antivirus?](./secops/what-is-edr-and-how-does-it-differ-from-antivirus.md) | 🟢 Beginner     |
| 176 | [What is SOAR and what should you automate first?](./secops/what-is-soar-and-what-should-you-automate-first.md)     | 🟡 Intermediate |

</details>

### 🧭 Platform and Leadership

_40 questions_

<details>
<summary><b>DevOps Culture and Practices</b> · 6 questions · 🟢 4 🟡 1 🔴 1</summary>

[Open the DevOps Culture and Practices index →](./devops-culture-and-practices/README.md)

| No. | Question                                                                                                                                  | Difficulty      |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 126 | [What is DevOps Culture?](./devops-culture-and-practices/what-is-devops-culture.md)                                                       | 🟢 Beginner     |
| 127 | [What are DevOps Best Practices?](./devops-culture-and-practices/what-are-devops-best-practices.md)                                       | 🟢 Beginner     |
| 128 | [What is Blameless Culture?](./devops-culture-and-practices/what-is-blameless-culture.md)                                                 | 🟡 Intermediate |
| 129 | [What is Knowledge Sharing in DevOps?](./devops-culture-and-practices/what-is-knowledge-sharing-in-devops.md)                             | 🟢 Beginner     |
| 130 | [What is Team Collaboration in DevOps?](./devops-culture-and-practices/what-is-team-collaboration-in-devops.md)                           | 🟢 Beginner     |
| 287 | [How do you scale DevOps culture across many teams?](./devops-culture-and-practices/how-do-you-scale-devops-culture-across-many-teams.md) | 🔴 Advanced     |

</details>

<details>
<summary><b>Advanced DevOps & Cloud</b> · 20 questions · 🟢 5 🟡 8 🔴 7</summary>

[Open the Advanced DevOps & Cloud index →](./advanced-devops-cloud/README.md)

| No. | Question                                                                                                       | Difficulty      |
| --- | -------------------------------------------------------------------------------------------------------------- | --------------- |
| 141 | [What is Platform Engineering?](./advanced-devops-cloud/what-is-platform-engineering.md)                       | 🔴 Advanced     |
| 142 | [What is FinOps?](./advanced-devops-cloud/what-is-finops.md)                                                   | 🟡 Intermediate |
| 143 | [What is Policy as Code?](./advanced-devops-cloud/what-is-policy-as-code.md)                                   | 🔴 Advanced     |
| 144 | [What is Chaos Engineering?](./advanced-devops-cloud/what-is-chaos-engineering.md)                             | 🔴 Advanced     |
| 145 | [What is Blue/Green Deployment?](./advanced-devops-cloud/what-is-blue-green-deployment.md)                     | 🟡 Intermediate |
| 146 | [What is Feature Flagging?](./advanced-devops-cloud/what-is-feature-flagging.md)                               | 🟡 Intermediate |
| 147 | [What is a Service Catalog?](./advanced-devops-cloud/what-is-a-service-catalog.md)                             | 🟡 Intermediate |
| 148 | [What is a Service Level Agreement (SLA)?](./advanced-devops-cloud/what-is-a-service-level-agreement-sla.md)   | 🟢 Beginner     |
| 149 | [What is a Service Level Objective (SLO)?](./advanced-devops-cloud/what-is-a-service-level-objective-slo.md)   | 🟢 Beginner     |
| 150 | [What is a Service Level Indicator (SLI)?](./advanced-devops-cloud/what-is-a-service-level-indicator-sli.md)   | 🟢 Beginner     |
| 151 | [What is a Runbook?](./advanced-devops-cloud/what-is-a-runbook.md)                                             | 🟢 Beginner     |
| 152 | [What is a Playbook in Incident Response?](./advanced-devops-cloud/what-is-a-playbook-in-incident-response.md) | 🟡 Intermediate |
| 153 | [What is Observability?](./advanced-devops-cloud/what-is-observability.md)                                     | 🔴 Advanced     |
| 154 | [What is Tracing in Observability?](./advanced-devops-cloud/what-is-tracing-in-observability.md)               | 🟡 Intermediate |
| 155 | [What is a Sidecar Pattern?](./advanced-devops-cloud/what-is-a-sidecar-pattern.md)                             | 🟡 Intermediate |
| 156 | [What is a Service Mesh Control Plane?](./advanced-devops-cloud/what-is-a-service-mesh-control-plane.md)       | 🔴 Advanced     |
| 157 | [What is GitHub Actions?](./advanced-devops-cloud/what-is-github-actions.md)                                   | 🟢 Beginner     |
| 158 | [What is a Self-Healing System?](./advanced-devops-cloud/what-is-a-self-healing-system.md)                     | 🔴 Advanced     |
| 159 | [What is Canary Analysis?](./advanced-devops-cloud/what-is-canary-analysis.md)                                 | 🔴 Advanced     |
| 160 | [What is Infrastructure Drift?](./advanced-devops-cloud/what-is-infrastructure-drift.md)                       | 🟡 Intermediate |

</details>

<details>
<summary><b>Platform Engineering</b> · 14 questions · 🟢 1 🟡 5 🔴 8</summary>

[Open the Platform Engineering index →](./platform-engineering/README.md)

| No. | Question                                                                                                                                                                                              | Difficulty      |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 222 | [What is an Internal Developer Platform (IDP)?](./platform-engineering/what-is-an-internal-developer-platform-idp.md)                                                                                 | 🟡 Intermediate |
| 223 | [What is a golden path?](./platform-engineering/what-is-a-golden-path.md)                                                                                                                             | 🟡 Intermediate |
| 224 | [How do you treat a platform as a product?](./platform-engineering/how-do-you-treat-a-platform-as-a-product.md)                                                                                       | 🔴 Advanced     |
| 225 | [What is Backstage?](./platform-engineering/what-is-backstage.md)                                                                                                                                     | 🟡 Intermediate |
| 226 | [What is Crossplane and how does it compare to Terraform?](./platform-engineering/what-is-crossplane-and-how-does-it-compare-to-terraform.md)                                                         | 🔴 Advanced     |
| 227 | [How do you provide self-service environments to developers?](./platform-engineering/how-do-you-provide-self-service-environments-to-developers.md)                                                   | 🔴 Advanced     |
| 228 | [How do you measure the success of a platform?](./platform-engineering/how-do-you-measure-the-success-of-a-platform.md)                                                                               | 🟡 Intermediate |
| 229 | [How do you roll out breaking platform changes safely?](./platform-engineering/how-do-you-roll-out-breaking-platform-changes-safely.md)                                                               | 🔴 Advanced     |
| 240 | [How do you orchestrate and autoscale GPU workloads in Kubernetes?](./platform-engineering/how-do-you-orchestrate-and-autoscale-gpu-workloads-in-kubernetes.md)                                       | 🔴 Advanced     |
| 241 | [How do you deploy and scale LLM inference serving with vLLM or Triton on Kubernetes?](./platform-engineering/how-do-you-deploy-and-scale-llm-inference-serving-with-vllm-or-triton-on-kubernetes.md) | 🔴 Advanced     |
| 242 | [How do you monitor AI/LLM applications for latency, GPU metrics, and token costs?](./platform-engineering/how-do-you-monitor-ai-llm-applications-for-latency-gpu-metrics-and-token-costs.md)         | 🟡 Intermediate |
| 243 | [How do you design a production MLOps pipeline using Ray or Kubeflow?](./platform-engineering/how-do-you-design-a-production-mlops-pipeline-using-ray-or-kubeflow.md)                                 | 🔴 Advanced     |
| 245 | [How do you deploy and scale Vector Databases in Kubernetes for RAG applications?](./platform-engineering/how-do-you-deploy-and-scale-vector-databases-in-kubernetes-for-rag-applications.md)         | 🔴 Advanced     |
| 299 | [What does a platform engineer actually do day to day?](./platform-engineering/what-does-a-platform-engineer-actually-do-day-to-day.md)                                                               | 🟢 Beginner     |

</details>

### 🎤 Interview Prep

_96 questions_

<details>
<summary><b>Interview Experience</b> · 96 questions · 🟢 5 🟡 28 🔴 63</summary>

[Open the Interview Experience index →](./interview-experience/README.md)

| No. | Question                                                                                                                                                                                          | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 271 | [How do you explain your DevOps project in an interview?](./interview-experience/how-do-you-explain-your-devops-project-in-an-interview.md)                                                       | 🟢 Beginner     |
| 272 | [What does a typical DevOps interview process look like?](./interview-experience/what-does-a-typical-devops-interview-process-look-like.md)                                                       | 🟢 Beginner     |
| 273 | [How do you answer scenario-based troubleshooting questions?](./interview-experience/how-do-you-answer-scenario-based-troubleshooting-questions.md)                                               | 🟡 Intermediate |
| 274 | [What are the most frequently asked DevOps interview questions?](./interview-experience/what-are-the-most-frequently-asked-devops-interview-questions.md)                                         | 🟢 Beginner     |
| 275 | [What questions should you ask your interviewer?](./interview-experience/what-questions-should-you-ask-your-interviewer.md)                                                                       | 🟢 Beginner     |
| 294 | [How do you handle a DevOps system design round?](./interview-experience/how-do-you-handle-a-devops-system-design-round.md)                                                                       | 🔴 Advanced     |
| 306 | [What DevOps interview questions does AMEX ask?](./interview-experience/what-devops-interview-questions-does-amex-ask.md)                                                                         | 🟡 Intermediate |
| 307 | [What DevOps interview questions does Accenture ask?](./interview-experience/what-devops-interview-questions-does-accenture-ask.md)                                                               | 🔴 Advanced     |
| 308 | [What SRE interview questions does Accion Labs ask?](./interview-experience/what-sre-interview-questions-does-accion-labs-ask.md)                                                                 | 🔴 Advanced     |
| 309 | [What DevOps interview questions does Accolite ask?](./interview-experience/what-devops-interview-questions-does-accolite-ask.md)                                                                 | 🟡 Intermediate |
| 310 | [What SRE interview questions does Akamai ask?](./interview-experience/what-sre-interview-questions-does-akamai-ask.md)                                                                           | 🔴 Advanced     |
| 311 | [What DevOps interview questions does Alphadyne ask?](./interview-experience/what-devops-interview-questions-does-alphadyne-ask.md)                                                               | 🔴 Advanced     |
| 312 | [What SRE interview questions does Altimetrik ask?](./interview-experience/what-sre-interview-questions-does-altimetrik-ask.md)                                                                   | 🔴 Advanced     |
| 313 | [What SRE interview questions does Amadeus Labs ask?](./interview-experience/what-sre-interview-questions-does-amadeus-labs-ask.md)                                                               | 🔴 Advanced     |
| 314 | [What DevOps consultant interview questions does Amazon ask?](./interview-experience/what-devops-consultant-interview-questions-does-amazon-ask.md)                                               | 🔴 Advanced     |
| 315 | [What DevOps interview questions does Arrise Solutions ask?](./interview-experience/what-devops-interview-questions-does-arrise-solutions-ask.md)                                                 | 🔴 Advanced     |
| 316 | [What DevOps interview questions does Aspire ask?](./interview-experience/what-devops-interview-questions-does-aspire-ask.md)                                                                     | 🟡 Intermediate |
| 317 | [What DevOps interview questions does BMW TechWorks ask?](./interview-experience/what-devops-interview-questions-does-bmw-techworks-ask.md)                                                       | 🟡 Intermediate |
| 318 | [What DevOps interview questions does Belcan ask?](./interview-experience/what-devops-interview-questions-does-belcan-ask.md)                                                                     | 🟡 Intermediate |
| 319 | [What DevOps interview questions does Blue Yonder ask?](./interview-experience/what-devops-interview-questions-does-blue-yonder-ask.md)                                                           | 🔴 Advanced     |
| 320 | [What DevOps interview questions does CGI ask?](./interview-experience/what-devops-interview-questions-does-cgi-ask.md)                                                                           | 🟡 Intermediate |
| 321 | [What SRE interview questions does CMT ask?](./interview-experience/what-sre-interview-questions-does-cmt-ask.md)                                                                                 | 🔴 Advanced     |
| 322 | [What DevOps interview questions does CTS Cognizant ask?](./interview-experience/what-devops-interview-questions-does-cts-cognizant-ask.md)                                                       | 🟡 Intermediate |
| 323 | [What DevOps interview questions does Capgemini ask?](./interview-experience/what-devops-interview-questions-does-capgemini-ask.md)                                                               | 🔴 Advanced     |
| 324 | [What DevOps interview questions does Cisco ask?](./interview-experience/what-devops-interview-questions-does-cisco-ask.md)                                                                       | 🔴 Advanced     |
| 325 | [What principal SRE interview questions does Commonwealth Bank ask?](./interview-experience/what-principal-sre-interview-questions-does-commonwealth-bank-ask.md)                                 | 🔴 Advanced     |
| 326 | [What DevOps interview questions does Deloitte ask?](./interview-experience/what-devops-interview-questions-does-deloitte-ask.md)                                                                 | 🔴 Advanced     |
| 327 | [What DevOps interview questions does EPAM ask?](./interview-experience/what-devops-interview-questions-does-epam-ask.md)                                                                         | 🔴 Advanced     |
| 328 | [What DevOps interview questions does EXL Service ask?](./interview-experience/what-devops-interview-questions-does-exl-service-ask.md)                                                           | 🔴 Advanced     |
| 329 | [What DevOps interview questions does EY ask?](./interview-experience/what-devops-interview-questions-does-ey-ask.md)                                                                             | 🟡 Intermediate |
| 330 | [What DevOps interview questions does Elixr Labs ask?](./interview-experience/what-devops-interview-questions-does-elixr-labs-ask.md)                                                             | 🔴 Advanced     |
| 331 | [What DevOps interview questions does Emphasis ask?](./interview-experience/what-devops-interview-questions-does-emphasis-ask.md)                                                                 | 🟡 Intermediate |
| 332 | [What DevOps interview questions does Encora ask?](./interview-experience/what-devops-interview-questions-does-encora-ask.md)                                                                     | 🔴 Advanced     |
| 333 | [What DevOps and cloud security interview questions does F5 ask?](./interview-experience/what-devops-and-cloud-security-interview-questions-does-f5-ask.md)                                       | 🔴 Advanced     |
| 334 | [What DevOps interview questions does Five9 ask?](./interview-experience/what-devops-interview-questions-does-five9-ask.md)                                                                       | 🔴 Advanced     |
| 335 | [What DevOps interview questions does Flentas ask?](./interview-experience/what-devops-interview-questions-does-flentas-ask.md)                                                                   | 🔴 Advanced     |
| 336 | [What DevOps interview questions does HCL ask?](./interview-experience/what-devops-interview-questions-does-hcl-ask.md)                                                                           | 🔴 Advanced     |
| 337 | [What DevOps interview questions does Hexaware ask?](./interview-experience/what-devops-interview-questions-does-hexaware-ask.md)                                                                 | 🟡 Intermediate |
| 338 | [What cloud and DevOps interview questions does IBM ask?](./interview-experience/what-cloud-and-devops-interview-questions-does-ibm-ask.md)                                                       | 🔴 Advanced     |
| 339 | [What DevOps interview questions does ITC Infotech ask?](./interview-experience/what-devops-interview-questions-does-itc-infotech-ask.md)                                                         | 🟡 Intermediate |
| 340 | [What DevOps interview questions does Infinite Solutions ask?](./interview-experience/what-devops-interview-questions-does-infinite-solutions-ask.md)                                             | 🟡 Intermediate |
| 341 | [What DevOps and SRE interview questions does Infosys ask?](./interview-experience/what-devops-and-sre-interview-questions-does-infosys-ask.md)                                                   | 🟡 Intermediate |
| 342 | [What DevOps interview questions does Intact Green Services ask?](./interview-experience/what-devops-interview-questions-does-intact-green-services-ask.md)                                       | 🔴 Advanced     |
| 343 | [What DevOps and SRE interview questions does JPMorgan ask?](./interview-experience/what-devops-and-sre-interview-questions-does-jpmorgan-ask.md)                                                 | 🔴 Advanced     |
| 344 | [What DevOps interview questions does Koerber Pharma ask?](./interview-experience/what-devops-interview-questions-does-koerber-pharma-ask.md)                                                     | 🔴 Advanced     |
| 345 | [What DevOps interview questions does LTIMindtree ask?](./interview-experience/what-devops-interview-questions-does-ltimindtree-ask.md)                                                           | 🔴 Advanced     |
| 346 | [What DevOps interview questions does L and T ask?](./interview-experience/what-devops-interview-questions-does-l-and-t-ask.md)                                                                   | 🟡 Intermediate |
| 347 | [What DevOps interview questions does Marsh McLennan ask?](./interview-experience/what-devops-interview-questions-does-marsh-mclennan-ask.md)                                                     | 🟡 Intermediate |
| 348 | [What MLOps interview questions does Moodys ask?](./interview-experience/what-mlops-interview-questions-does-moodys-ask.md)                                                                       | 🔴 Advanced     |
| 349 | [What release engineering interview questions does Morgan Stanley ask?](./interview-experience/what-release-engineering-interview-questions-does-morgan-stanley-ask.md)                           | 🔴 Advanced     |
| 350 | [What DevOps interview questions does NPCI ask?](./interview-experience/what-devops-interview-questions-does-npci-ask.md)                                                                         | 🔴 Advanced     |
| 351 | [What DevOps interview questions does NUOS INFO Systems ask?](./interview-experience/what-devops-interview-questions-does-nuos-info-systems-ask.md)                                               | 🔴 Advanced     |
| 352 | [What DevOps interview questions does NatWest Group ask?](./interview-experience/what-devops-interview-questions-does-natwest-group-ask.md)                                                       | 🟡 Intermediate |
| 353 | [What DevOps interview questions does Netcracker ask?](./interview-experience/what-devops-interview-questions-does-netcracker-ask.md)                                                             | 🔴 Advanced     |
| 354 | [What DevOps interview questions does Nextturn ask?](./interview-experience/what-devops-interview-questions-does-nextturn-ask.md)                                                                 | 🔴 Advanced     |
| 355 | [What cloud SRE interview questions does Nice ask?](./interview-experience/what-cloud-sre-interview-questions-does-nice-ask.md)                                                                   | 🟡 Intermediate |
| 356 | [What DevOps interview questions does Nisum Technologies ask?](./interview-experience/what-devops-interview-questions-does-nisum-technologies-ask.md)                                             | 🟡 Intermediate |
| 357 | [What DevOps interview questions does Nitor Infotech ask?](./interview-experience/what-devops-interview-questions-does-nitor-infotech-ask.md)                                                     | 🔴 Advanced     |
| 358 | [What DevOps interview questions does OPT IT ask?](./interview-experience/what-devops-interview-questions-does-opt-it-ask.md)                                                                     | 🟡 Intermediate |
| 359 | [What DevOps interview questions does One2N ask?](./interview-experience/what-devops-interview-questions-does-one2n-ask.md)                                                                       | 🔴 Advanced     |
| 360 | [What DevOps interview questions does Optum ask?](./interview-experience/what-devops-interview-questions-does-optum-ask.md)                                                                       | 🔴 Advanced     |
| 361 | [What DevOps interview questions does Oracle ask?](./interview-experience/what-devops-interview-questions-does-oracle-ask.md)                                                                     | 🔴 Advanced     |
| 362 | [What DevOps interview questions does Orion Innovation ask?](./interview-experience/what-devops-interview-questions-does-orion-innovation-ask.md)                                                 | 🟡 Intermediate |
| 363 | [What cloud engineering interview questions come up when the company is not named?](./interview-experience/what-cloud-engineering-interview-questions-come-up-when-the-company-is-not-named.md)   | 🔴 Advanced     |
| 364 | [What SRE interview questions come up when the company is not named?](./interview-experience/what-sre-interview-questions-come-up-when-the-company-is-not-named.md)                               | 🟡 Intermediate |
| 365 | [What behavioural DevOps interview questions come up when the company is not named?](./interview-experience/what-behavioural-devops-interview-questions-come-up-when-the-company-is-not-named.md) | 🟡 Intermediate |
| 366 | [What DevOps interview questions come up when the company is not named?](./interview-experience/what-devops-interview-questions-come-up-when-the-company-is-not-named.md)                         | 🔴 Advanced     |
| 367 | [What DevOps scenario and pipeline questions come up when the company is not named?](./interview-experience/what-devops-scenario-and-pipeline-questions-come-up-when-the-company-is-not-named.md) | 🔴 Advanced     |
| 368 | [What DevOps interview questions does Perfios ask?](./interview-experience/what-devops-interview-questions-does-perfios-ask.md)                                                                   | 🔴 Advanced     |
| 369 | [What DevOps interview questions does Persistent Systems ask?](./interview-experience/what-devops-interview-questions-does-persistent-systems-ask.md)                                             | 🔴 Advanced     |
| 370 | [What DevOps interview questions does Plansource ValueLabs ask?](./interview-experience/what-devops-interview-questions-does-plansource-valuelabs-ask.md)                                         | 🔴 Advanced     |
| 371 | [What DevOps interview questions does Publicis Global Delivery ask?](./interview-experience/what-devops-interview-questions-does-publicis-global-delivery-ask.md)                                 | 🔴 Advanced     |
| 372 | [What DevOps interview questions does Qburst ask?](./interview-experience/what-devops-interview-questions-does-qburst-ask.md)                                                                     | 🔴 Advanced     |
| 373 | [What DevOps interview questions does Qentelli Solutions ask?](./interview-experience/what-devops-interview-questions-does-qentelli-solutions-ask.md)                                             | 🟡 Intermediate |
| 374 | [What DevOps interview questions does Rapidsoft ask?](./interview-experience/what-devops-interview-questions-does-rapidsoft-ask.md)                                                               | 🟡 Intermediate |
| 375 | [What DevOps interview questions does RelevantZ ask?](./interview-experience/what-devops-interview-questions-does-relevantz-ask.md)                                                               | 🔴 Advanced     |
| 376 | [What DevOps interview questions does SAP ask?](./interview-experience/what-devops-interview-questions-does-sap-ask.md)                                                                           | 🔴 Advanced     |
| 377 | [What DevOps interview questions does Sapient ask?](./interview-experience/what-devops-interview-questions-does-sapient-ask.md)                                                                   | 🔴 Advanced     |
| 378 | [What DevOps interview questions does Sigmoid ask?](./interview-experience/what-devops-interview-questions-does-sigmoid-ask.md)                                                                   | 🔴 Advanced     |
| 379 | [What DevOps interview questions does Sonata Software ask?](./interview-experience/what-devops-interview-questions-does-sonata-software-ask.md)                                                   | 🔴 Advanced     |
| 380 | [What DevOps interview questions does Sony ask?](./interview-experience/what-devops-interview-questions-does-sony-ask.md)                                                                         | 🔴 Advanced     |
| 381 | [What DevOps interview questions does SquareOps ask?](./interview-experience/what-devops-interview-questions-does-squareops-ask.md)                                                               | 🔴 Advanced     |
| 382 | [What release engineering interview questions does Syncortex ask?](./interview-experience/what-release-engineering-interview-questions-does-syncortex-ask.md)                                     | 🔴 Advanced     |
| 383 | [What DevOps interview questions does Synechron ask?](./interview-experience/what-devops-interview-questions-does-synechron-ask.md)                                                               | 🔴 Advanced     |
| 384 | [What DevOps and SRE interview questions does TCS ask?](./interview-experience/what-devops-and-sre-interview-questions-does-tcs-ask.md)                                                           | 🔴 Advanced     |
| 385 | [What DevOps interview questions does Techdome ask?](./interview-experience/what-devops-interview-questions-does-techdome-ask.md)                                                                 | 🟡 Intermediate |
| 386 | [What cloud engineering interview questions does Turning ask?](./interview-experience/what-cloud-engineering-interview-questions-does-turning-ask.md)                                             | 🔴 Advanced     |
| 387 | [What cloud platform engineering interview questions does UST ask?](./interview-experience/what-cloud-platform-engineering-interview-questions-does-ust-ask.md)                                   | 🔴 Advanced     |
| 388 | [What DevOps interview questions does Verizon ask?](./interview-experience/what-devops-interview-questions-does-verizon-ask.md)                                                                   | 🔴 Advanced     |
| 389 | [What DevOps tech lead interview questions does Virtusa ask?](./interview-experience/what-devops-tech-lead-interview-questions-does-virtusa-ask.md)                                               | 🔴 Advanced     |
| 390 | [What DevOps interview questions does Volkswagen Group Digital ask?](./interview-experience/what-devops-interview-questions-does-volkswagen-group-digital-ask.md)                                 | 🔴 Advanced     |
| 391 | [What DevOps interview questions does Wikreate Media ask?](./interview-experience/what-devops-interview-questions-does-wikreate-media-ask.md)                                                     | 🟢 Beginner     |
| 392 | [What DevOps interview questions does Wipro ask?](./interview-experience/what-devops-interview-questions-does-wipro-ask.md)                                                                       | 🔴 Advanced     |
| 393 | [What DevOps interview questions does ZS Associates ask?](./interview-experience/what-devops-interview-questions-does-zs-associates-ask.md)                                                       | 🔴 Advanced     |
| 394 | [What DevOps interview questions does Zensar ask?](./interview-experience/what-devops-interview-questions-does-zensar-ask.md)                                                                     | 🟡 Intermediate |
| 395 | [What DevOps interview questions does ZopSmart ask?](./interview-experience/what-devops-interview-questions-does-zopsmart-ask.md)                                                                 | 🟡 Intermediate |

</details>

<!-- TOC:END -->

---

## 🧠 How answers are structured

Every answer follows the same four beats, so you can read one section deep or all four:

| Section            | What it gives you                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| **Short answer**   | Two or three sentences you could say out loud. Start here.                                                    |
| **Detail**         | The substance - mechanisms, trade-offs, and the vocabulary that signals experience.                           |
| **Example**        | Real commands, YAML, or code you can run and adapt.                                                           |
| **Interview tips** | The follow-up questions, the common traps, and the points that separate a strong answer from a memorised one. |

Difficulty is marked 🟢 Beginner · 🟡 Intermediate · 🔴 Advanced.

**Three ways to work through it:**

- **Preparing for a specific role** - take the track from [Pick your role](#-pick-your-role), and read each topic README's "What interviewers probe here" before its questions.
- **Broad revision** - read the short answers across a topic, then go deep only where you hesitate.
- **Obsidian / note vault** - every file carries YAML frontmatter (`title`, `id`, `category`, `difficulty`, `tags`), so the whole repository can be dropped into a vault and browsed by tag.

---

## 🛠️ Repository structure

```text
.
├── core-devops-concepts/           # topic-slug/
│   ├── README.md                   #   generated topic index
│   └── what-is-devops.md           #   question-slug.md
├── ...
├── scripts/
│   ├── lib_content.py              # shared frontmatter/vault parsing
│   ├── generate_indexes.py         # regenerates all indexes from question files
│   ├── validate_content.py         # CI validation of the whole vault
│   └── topic_meta.json             # topic registry: order, group, description, study notes
└── .github/workflows/
    └── validate-and-format.yml     # runs validation + Prettier on every PR
```

Directories and filenames carry **no numeric prefixes** - they are pure slugs. Ordering comes from two places instead:

- **Topic order** - the `order` field in `scripts/topic_meta.json`, which is also the registry of which directories count as topics.
- **Question order** - the `id` field in each question's frontmatter, unique across the repository.

Renaming or reordering is therefore a metadata edit, not a mass file rename.

Every question file starts with frontmatter:

```yaml
---
title: "What is Kubernetes?"
id: 11
category: "Kubernetes"
difficulty: "Beginner"
tags:
  - devops
  - kubernetes
  - interview-questions
---
```

**The indexes are generated, not hand-written.** The question files are the single source of truth; topic READMEs and the tables above are rendered from their frontmatter. After adding or editing a question:

```bash
python3 scripts/generate_indexes.py     # rewrite all indexes
python3 scripts/validate_content.py     # verify frontmatter, naming, links, index freshness
```

Both are stdlib-only Python 3.11+ - no dependencies to install. CI runs the same commands and fails the pull request on drift.

---

## 🤝 Contributing

New questions, better answers, and corrections are all welcome. [CONTRIBUTING.md](./CONTRIBUTING.md) covers the file format, naming rules, and the local checks to run before opening a pull request.

Not sure where to start? Open an issue - there are templates for [a new question](https://github.com/mchittineni/ultimate-devops-guide/issues/new?template=1-new-question.yml), [a correction to an existing answer](https://github.com/mchittineni/ultimate-devops-guide/issues/new?template=2-improve-answer.yml), and [an interview experience to add](https://github.com/mchittineni/ultimate-devops-guide/issues/new?template=3-interview-experience.yml).

Two documents set the ground rules: the [Code of Conduct](./CODE_OF_CONDUCT.md) - including the rules on interviewer privacy, NDAs, and plagiarism that apply to interview write-ups - and the [Security Policy](./SECURITY.md), which covers how to report a committed credential or a workflow vulnerability privately.

## 🙏 Acknowledgements & Inspiration

Special thanks and heartfelt gratitude to the creators and maintainers of the following open-source repositories and community resources whose work provided inspiration, practical insights, and foundational ideas for this project:

- **[rohitg00/devops-interview-questions](https://github.com/rohitg00/devops-interview-questions)** – Comprehensive DevOps interview questions repository.
- **[bregman-arie/devops-exercises](https://github.com/bregman-arie/devops-exercises)** – Extensive collection of DevOps exercises, diagrams, and practical questions.
- **[tikam02/devops-guide](https://github.com/tikam02/devops-guide)** – Practical guide for DevOps configurations, cheat sheets, and systems management.
- **[NotHarshhaa/AWS-GCP-Azure-Cloud-Projects-Workshop](https://github.com/NotHarshhaa/AWS-GCP-Azure-Cloud-Projects-Workshop)** – Hands-on multi-cloud architecture projects and workshop guides.
- **[NotHarshhaa/DevOps-Projects](https://github.com/NotHarshhaa/DevOps-Projects)** – Practical real-world DevOps project blueprints and automation pipelines.
- **[NotHarshhaa/DevOps-Interview-Questions](https://github.com/NotHarshhaa/DevOps-Interview-Questions)** – Collection of 1100+ DevOps interview questions with detailed answers and solutions.
- **[iam-veeramalla/devops-interview-preparation-guide](https://github.com/iam-veeramalla/devops-interview-preparation-guide)** – Detailed interview preparation guide and practical scenario breakdowns.
- **[litu54/DevOps-Interview-Guide](https://github.com/litu54/DevOps-Interview-Guide)** – Real-world company interview experiences and question collections.

## 📄 License

Released under the [MIT License](./LICENSE).
