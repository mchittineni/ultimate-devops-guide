# DevOps Interview Questions & Answers

> A curated, structured set of DevOps interview questions with answers written to the depth an interviewer actually expects — definition, detail, a worked example, and the follow-ups you should be ready for.

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
![Questions](https://img.shields.io/badge/questions-233-blue)
![Topics](https://img.shields.io/badge/topics-38-blueviolet)
![License](https://img.shields.io/badge/license-MIT-green)

⭐ Star the project if it helps you. Pull requests are very welcome — see [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## How to use this repository

Every question lives in its own file under a numbered topic directory, and every answer follows the same shape:

| Section            | What it gives you                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| **Short answer**   | Two or three sentences you could say out loud. Start here.                                                    |
| **Detail**         | The substance — mechanisms, trade-offs, and the vocabulary that signals experience.                           |
| **Example**        | Real commands, YAML, or code you can run and adapt.                                                           |
| **Interview tips** | The follow-up questions, the common traps, and the points that separate a strong answer from a memorised one. |

Difficulty is marked 🟢 Beginner · 🟡 Intermediate · 🔴 Advanced.

**Three ways to work through it:**

- **Preparing for a specific role** — jump to the relevant topic README and read its "What interviewers probe here" section first, then the questions.
- **Broad revision** — read the short answers across a topic, then go deep only where you hesitate.
- **Obsidian / note vault** — every file carries YAML frontmatter (`title`, `id`, `category`, `difficulty`, `tags`), so the whole repository can be dropped into a vault and browsed by tag.

### Suggested study paths

| Target role                   | Start with these topics                                                                                                                                                                                                                                                                  |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Junior / Associate DevOps** | [Core Concepts](./core-devops-concepts/README.md) → [Docker](./docker/README.md) → [Linux](./linux-administration/README.md) → [Version Control](./version-control/README.md) → [CI/CD](./cicd/README.md)                                                                                |
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

## Repository at a glance

<!-- STATS:START -->

**233 questions** across **38 topics** — 🟢 81 Beginner · 🟡 117 Intermediate · 🔴 35 Advanced

| Topic                                                                              | Directory                           | Questions | 🟢  | 🟡  | 🔴  |
| ---------------------------------------------------------------------------------- | ----------------------------------- | --------- | --- | --- | --- |
| [Core DevOps Concepts](./core-devops-concepts/README.md)                           | `core-devops-concepts`              | 5         | 4   | 1   | 0   |
| [Docker](./docker/README.md)                                                       | `docker`                            | 5         | 4   | 1   | 0   |
| [Kubernetes](./kubernetes/README.md)                                               | `kubernetes`                        | 5         | 3   | 2   | 0   |
| [CI/CD](./cicd/README.md)                                                          | `cicd`                              | 5         | 2   | 3   | 0   |
| [Cloud Platforms](./cloud-platforms/README.md)                                     | `cloud-platforms`                   | 5         | 5   | 0   | 0   |
| [Infrastructure as Code](./infrastructure-as-code/README.md)                       | `infrastructure-as-code`            | 5         | 3   | 2   | 0   |
| [Monitoring and Logging](./monitoring-and-logging/README.md)                       | `monitoring-and-logging`            | 5         | 4   | 1   | 0   |
| [Security and Compliance](./security-and-compliance/README.md)                     | `security-and-compliance`           | 5         | 1   | 3   | 1   |
| [Linux Administration](./linux-administration/README.md)                           | `linux-administration`              | 5         | 4   | 1   | 0   |
| [Version Control](./version-control/README.md)                                     | `version-control`                   | 5         | 2   | 3   | 0   |
| [Configuration Management](./configuration-management/README.md)                   | `configuration-management`          | 5         | 1   | 4   | 0   |
| [Scalability and High Availability](./scalability-and-high-availability/README.md) | `scalability-and-high-availability` | 5         | 4   | 1   | 0   |
| [Backup and Disaster Recovery](./backup-and-disaster-recovery/README.md)           | `backup-and-disaster-recovery`      | 5         | 4   | 1   | 0   |
| [Cloud Native Architecture](./cloud-native-architecture/README.md)                 | `cloud-native-architecture`         | 5         | 0   | 4   | 1   |
| [Performance Testing](./performance-testing/README.md)                             | `performance-testing`               | 5         | 3   | 2   | 0   |
| [API Gateway and Service Mesh](./api-gateway-and-service-mesh/README.md)           | `api-gateway-and-service-mesh`      | 5         | 3   | 2   | 0   |
| [Container Orchestration Advanced](./container-orchestration-advanced/README.md)   | `container-orchestration-advanced`  | 5         | 0   | 2   | 3   |
| [DevOps Tools and Automation](./devops-tools-and-automation/README.md)             | `devops-tools-and-automation`       | 5         | 1   | 4   | 0   |
| [Cloud Cost Optimization](./cloud-cost-optimization/README.md)                     | `cloud-cost-optimization`           | 5         | 2   | 3   | 0   |
| [Site Reliability Engineering (SRE)](./site-reliability-engineering/README.md)     | `site-reliability-engineering`      | 9         | 1   | 6   | 2   |
| [DevOps Metrics and KPIs](./devops-metrics-and-kpis/README.md)                     | `devops-metrics-and-kpis`           | 5         | 3   | 2   | 0   |
| [Serverless Architecture](./serverless-architecture/README.md)                     | `serverless-architecture`           | 5         | 4   | 1   | 0   |
| [Database Management in DevOps](./database-management-in-devops/README.md)         | `database-management-in-devops`     | 5         | 0   | 4   | 1   |
| [Network Security](./network-security/README.md)                                   | `network-security`                  | 5         | 2   | 3   | 0   |
| [Incident Management](./incident-management/README.md)                             | `incident-management`               | 5         | 2   | 3   | 0   |
| [DevOps Culture and Practices](./devops-culture-and-practices/README.md)           | `devops-culture-and-practices`      | 5         | 4   | 1   | 0   |
| [Infrastructure Monitoring](./infrastructure-monitoring/README.md)                 | `infrastructure-monitoring`         | 5         | 2   | 3   | 0   |
| [Cloud Migration](./cloud-migration/README.md)                                     | `cloud-migration`                   | 5         | 1   | 4   | 0   |
| [Advanced DevOps & Cloud](./advanced-devops-cloud/README.md)                       | `advanced-devops-cloud`             | 20        | 5   | 8   | 7   |
| [DevSecOps](./devsecops/README.md)                                                 | `devsecops`                         | 8         | 0   | 6   | 2   |
| [SecOps and Threat Detection](./secops/README.md)                                  | `secops`                            | 8         | 2   | 4   | 2   |
| [SLO Engineering](./slo-engineering/README.md)                                     | `slo-engineering`                   | 7         | 0   | 3   | 4   |
| [SLA Management](./sla-management/README.md)                                       | `sla-management`                    | 7         | 2   | 4   | 1   |
| [AWS Engineering](./aws-engineering/README.md)                                     | `aws-engineering`                   | 8         | 0   | 5   | 3   |
| [Azure Engineering](./azure-engineering/README.md)                                 | `azure-engineering`                 | 8         | 1   | 6   | 1   |
| [GCP Engineering](./gcp-engineering/README.md)                                     | `gcp-engineering`                   | 8         | 1   | 7   | 0   |
| [Cloud Engineering](./cloud-engineering/README.md)                                 | `cloud-engineering`                 | 7         | 1   | 3   | 3   |
| [Platform Engineering](./platform-engineering/README.md)                           | `platform-engineering`              | 8         | 0   | 4   | 4   |

<!-- STATS:END -->

---

## Table of Contents

<details open>
<summary>Hide/Show table of contents</summary>

<!-- TOC:START -->

| No. | Question                                                                                                                                                                      | Difficulty      |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
|     | **[Core DevOps Concepts](./core-devops-concepts/README.md)** (5)                                                                                                              |                 |
| 1   | [What is DevOps?](./core-devops-concepts/what-is-devops.md)                                                                                                                   | 🟢 Beginner     |
| 2   | [What are the benefits of DevOps?](./core-devops-concepts/what-are-the-benefits-of-devops.md)                                                                                 | 🟢 Beginner     |
| 3   | [What is Continuous Integration?](./core-devops-concepts/what-is-continuous-integration.md)                                                                                   | 🟢 Beginner     |
| 4   | [What is Continuous Delivery?](./core-devops-concepts/what-is-continuous-delivery.md)                                                                                         | 🟢 Beginner     |
| 5   | [What is Continuous Deployment?](./core-devops-concepts/what-is-continuous-deployment.md)                                                                                     | 🟡 Intermediate |
|     | **[Docker](./docker/README.md)** (5)                                                                                                                                          |                 |
| 6   | [What is Docker?](./docker/what-is-docker.md)                                                                                                                                 | 🟢 Beginner     |
| 7   | [What is the difference between Docker Image and Docker Container?](./docker/what-is-the-difference-between-docker-image-and-docker-container.md)                             | 🟢 Beginner     |
| 8   | [What is Dockerfile?](./docker/what-is-dockerfile.md)                                                                                                                         | 🟢 Beginner     |
| 9   | [What is Docker Compose?](./docker/what-is-docker-compose.md)                                                                                                                 | 🟢 Beginner     |
| 10  | [Explain Docker Architecture](./docker/explain-docker-architecture.md)                                                                                                        | 🟡 Intermediate |
|     | **[Kubernetes](./kubernetes/README.md)** (5)                                                                                                                                  |                 |
| 11  | [What is Kubernetes?](./kubernetes/what-is-kubernetes.md)                                                                                                                     | 🟢 Beginner     |
| 12  | [What are the main components of Kubernetes architecture?](./kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)                                           | 🟡 Intermediate |
| 13  | [What is a Pod in Kubernetes?](./kubernetes/what-is-a-pod-in-kubernetes.md)                                                                                                   | 🟢 Beginner     |
| 14  | [What is a Service in Kubernetes?](./kubernetes/what-is-a-service-in-kubernetes.md)                                                                                           | 🟢 Beginner     |
| 15  | [Explain the difference between Docker Swarm and Kubernetes](./kubernetes/explain-the-difference-between-docker-swarm-and-kubernetes.md)                                      | 🟡 Intermediate |
|     | **[CI/CD](./cicd/README.md)** (5)                                                                                                                                             |                 |
| 16  | [What is CI/CD Pipeline?](./cicd/what-is-ci-cd-pipeline.md)                                                                                                                   | 🟢 Beginner     |
| 17  | [What is Jenkins?](./cicd/what-is-jenkins.md)                                                                                                                                 | 🟢 Beginner     |
| 18  | [What are Jenkins Pipelines?](./cicd/what-are-jenkins-pipelines.md)                                                                                                           | 🟡 Intermediate |
| 19  | [What is GitLab CI?](./cicd/what-is-gitlab-ci.md)                                                                                                                             | 🟡 Intermediate |
| 20  | [What is the difference between Continuous Delivery and Continuous Deployment?](./cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)       | 🟡 Intermediate |
|     | **[Cloud Platforms](./cloud-platforms/README.md)** (5)                                                                                                                        |                 |
| 21  | [What is Cloud Computing?](./cloud-platforms/what-is-cloud-computing.md)                                                                                                      | 🟢 Beginner     |
| 22  | [What is AWS (Amazon Web Services)?](./cloud-platforms/what-is-aws-amazon-web-services.md)                                                                                    | 🟢 Beginner     |
| 23  | [What is Azure?](./cloud-platforms/what-is-azure.md)                                                                                                                          | 🟢 Beginner     |
| 24  | [What is Google Cloud Platform (GCP)?](./cloud-platforms/what-is-google-cloud-platform-gcp.md)                                                                                | 🟢 Beginner     |
| 25  | [What are the different types of cloud services?](./cloud-platforms/what-are-the-different-types-of-cloud-services.md)                                                        | 🟢 Beginner     |
|     | **[Infrastructure as Code](./infrastructure-as-code/README.md)** (5)                                                                                                          |                 |
| 26  | [What is Infrastructure as Code?](./infrastructure-as-code/what-is-infrastructure-as-code.md)                                                                                 | 🟢 Beginner     |
| 27  | [What is Terraform?](./infrastructure-as-code/what-is-terraform.md)                                                                                                           | 🟢 Beginner     |
| 28  | [What is Ansible?](./infrastructure-as-code/what-is-ansible.md)                                                                                                               | 🟢 Beginner     |
| 29  | [What is the difference between Ansible and Terraform?](./infrastructure-as-code/what-is-the-difference-between-ansible-and-terraform.md)                                     | 🟡 Intermediate |
| 30  | [What are Terraform providers?](./infrastructure-as-code/what-are-terraform-providers.md)                                                                                     | 🟡 Intermediate |
|     | **[Monitoring and Logging](./monitoring-and-logging/README.md)** (5)                                                                                                          |                 |
| 31  | [What is monitoring in DevOps?](./monitoring-and-logging/what-is-monitoring-in-devops.md)                                                                                     | 🟢 Beginner     |
| 32  | [What is ELK Stack?](./monitoring-and-logging/what-is-elk-stack.md)                                                                                                           | 🟡 Intermediate |
| 33  | [What is Prometheus?](./monitoring-and-logging/what-is-prometheus.md)                                                                                                         | 🟢 Beginner     |
| 34  | [What is Grafana?](./monitoring-and-logging/what-is-grafana.md)                                                                                                               | 🟢 Beginner     |
| 35  | [Explain the difference between monitoring and logging](./monitoring-and-logging/explain-the-difference-between-monitoring-and-logging.md)                                    | 🟢 Beginner     |
|     | **[Security and Compliance](./security-and-compliance/README.md)** (5)                                                                                                        |                 |
| 36  | [What is DevSecOps?](./security-and-compliance/what-is-devsecops.md)                                                                                                          | 🟢 Beginner     |
| 37  | [What is Infrastructure Security?](./security-and-compliance/what-is-infrastructure-security.md)                                                                              | 🟡 Intermediate |
| 38  | [What is Container Security?](./security-and-compliance/what-is-container-security.md)                                                                                        | 🟡 Intermediate |
| 39  | [What is Compliance as Code?](./security-and-compliance/what-is-compliance-as-code.md)                                                                                        | 🔴 Advanced     |
| 40  | [What are Security Best Practices in DevOps?](./security-and-compliance/what-are-security-best-practices-in-devops.md)                                                        | 🟡 Intermediate |
|     | **[Linux Administration](./linux-administration/README.md)** (5)                                                                                                              |                 |
| 41  | [What are the basic Linux commands every DevOps engineer should know?](./linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md)         | 🟢 Beginner     |
| 42  | [What is Shell Scripting?](./linux-administration/what-is-shell-scripting.md)                                                                                                 | 🟢 Beginner     |
| 43  | [What is systemd?](./linux-administration/what-is-systemd.md)                                                                                                                 | 🟡 Intermediate |
| 44  | [How do you manage services in Linux?](./linux-administration/how-do-you-manage-services-in-linux.md)                                                                         | 🟢 Beginner     |
| 45  | [What is Linux File System Hierarchy?](./linux-administration/what-is-linux-file-system-hierarchy.md)                                                                         | 🟢 Beginner     |
|     | **[Version Control](./version-control/README.md)** (5)                                                                                                                        |                 |
| 46  | [What is Git?](./version-control/what-is-git.md)                                                                                                                              | 🟢 Beginner     |
| 47  | [What is Git Branching Strategy?](./version-control/what-is-git-branching-strategy.md)                                                                                        | 🟡 Intermediate |
| 48  | [What is Git Flow?](./version-control/what-is-git-flow.md)                                                                                                                    | 🟡 Intermediate |
| 49  | [What is Trunk Based Development?](./version-control/what-is-trunk-based-development.md)                                                                                      | 🟡 Intermediate |
| 50  | [How to handle merge conflicts in Git?](./version-control/how-to-handle-merge-conflicts-in-git.md)                                                                            | 🟢 Beginner     |
|     | **[Configuration Management](./configuration-management/README.md)** (5)                                                                                                      |                 |
| 51  | [What is Configuration Management?](./configuration-management/what-is-configuration-management.md)                                                                           | 🟢 Beginner     |
| 52  | [What is Puppet?](./configuration-management/what-is-puppet.md)                                                                                                               | 🟡 Intermediate |
| 53  | [What is Chef?](./configuration-management/what-is-chef.md)                                                                                                                   | 🟡 Intermediate |
| 54  | [What is Salt (SaltStack)?](./configuration-management/what-is-salt-saltstack.md)                                                                                             | 🟡 Intermediate |
| 55  | [Compare different Configuration Management tools](./configuration-management/compare-different-configuration-management-tools.md)                                            | 🟡 Intermediate |
|     | **[Scalability and High Availability](./scalability-and-high-availability/README.md)** (5)                                                                                    |                 |
| 56  | [What is Scalability in DevOps?](./scalability-and-high-availability/what-is-scalability-in-devops.md)                                                                        | 🟢 Beginner     |
| 57  | [What is High Availability?](./scalability-and-high-availability/what-is-high-availability.md)                                                                                | 🟢 Beginner     |
| 58  | [What is Load Balancing?](./scalability-and-high-availability/what-is-load-balancing.md)                                                                                      | 🟢 Beginner     |
| 59  | [What is Auto Scaling?](./scalability-and-high-availability/what-is-auto-scaling.md)                                                                                          | 🟢 Beginner     |
| 60  | [What is Disaster Recovery?](./scalability-and-high-availability/what-is-disaster-recovery.md)                                                                                | 🟡 Intermediate |
|     | **[Backup and Disaster Recovery](./backup-and-disaster-recovery/README.md)** (5)                                                                                              |                 |
| 61  | [What is Backup and Disaster Recovery?](./backup-and-disaster-recovery/what-is-backup-and-disaster-recovery.md)                                                               | 🟢 Beginner     |
| 62  | [What are different types of backups?](./backup-and-disaster-recovery/what-are-different-types-of-backups.md)                                                                 | 🟢 Beginner     |
| 63  | [What is RPO and RTO?](./backup-and-disaster-recovery/what-is-rpo-and-rto.md)                                                                                                 | 🟢 Beginner     |
| 64  | [What is Business Continuity Planning?](./backup-and-disaster-recovery/what-is-business-continuity-planning.md)                                                               | 🟡 Intermediate |
| 65  | [What are backup best practices?](./backup-and-disaster-recovery/what-are-backup-best-practices.md)                                                                           | 🟢 Beginner     |
|     | **[Cloud Native Architecture](./cloud-native-architecture/README.md)** (5)                                                                                                    |                 |
| 66  | [What is Cloud Native Architecture?](./cloud-native-architecture/what-is-cloud-native-architecture.md)                                                                        | 🟡 Intermediate |
| 67  | [What are Microservices?](./cloud-native-architecture/what-are-microservices.md)                                                                                              | 🟡 Intermediate |
| 68  | [What is Service Mesh?](./cloud-native-architecture/what-is-service-mesh.md)                                                                                                  | 🔴 Advanced     |
| 69  | [What is Event-Driven Architecture?](./cloud-native-architecture/what-is-event-driven-architecture.md)                                                                        | 🟡 Intermediate |
| 70  | [What are the 12-Factor App principles?](./cloud-native-architecture/what-are-the-12-factor-app-principles.md)                                                                | 🟡 Intermediate |
|     | **[Performance Testing](./performance-testing/README.md)** (5)                                                                                                                |                 |
| 71  | [What is Performance Testing?](./performance-testing/what-is-performance-testing.md)                                                                                          | 🟢 Beginner     |
| 72  | [What are different types of Performance Tests?](./performance-testing/what-are-different-types-of-performance-tests.md)                                                      | 🟢 Beginner     |
| 73  | [What are Performance Testing Tools?](./performance-testing/what-are-performance-testing-tools.md)                                                                            | 🟢 Beginner     |
| 74  | [What are Performance Testing Best Practices?](./performance-testing/what-are-performance-testing-best-practices.md)                                                          | 🟡 Intermediate |
| 75  | [How to analyze Performance Test Results?](./performance-testing/how-to-analyze-performance-test-results.md)                                                                  | 🟡 Intermediate |
|     | **[API Gateway and Service Mesh](./api-gateway-and-service-mesh/README.md)** (5)                                                                                              |                 |
| 76  | [What is an API Gateway?](./api-gateway-and-service-mesh/what-is-an-api-gateway.md)                                                                                           | 🟡 Intermediate |
| 77  | [What are the benefits of using API Gateway?](./api-gateway-and-service-mesh/what-are-the-benefits-of-using-api-gateway.md)                                                   | 🟢 Beginner     |
| 78  | [What is API Security?](./api-gateway-and-service-mesh/what-is-api-security.md)                                                                                               | 🟡 Intermediate |
| 79  | [What is Rate Limiting?](./api-gateway-and-service-mesh/what-is-rate-limiting.md)                                                                                             | 🟢 Beginner     |
| 80  | [What is API Documentation?](./api-gateway-and-service-mesh/what-is-api-documentation.md)                                                                                     | 🟢 Beginner     |
|     | **[Container Orchestration Advanced](./container-orchestration-advanced/README.md)** (5)                                                                                      |                 |
| 81  | [What are StatefulSets in Kubernetes?](./container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md)                                                             | 🔴 Advanced     |
| 82  | [What are DaemonSets in Kubernetes?](./container-orchestration-advanced/what-are-daemonsets-in-kubernetes.md)                                                                 | 🟡 Intermediate |
| 83  | [What is Helm?](./container-orchestration-advanced/what-is-helm.md)                                                                                                           | 🟡 Intermediate |
| 84  | [What is Istio?](./container-orchestration-advanced/what-is-istio.md)                                                                                                         | 🔴 Advanced     |
| 85  | [What is Container Runtime Interface (CRI)?](./container-orchestration-advanced/what-is-container-runtime-interface-cri.md)                                                   | 🔴 Advanced     |
|     | **[DevOps Tools and Automation](./devops-tools-and-automation/README.md)** (5)                                                                                                |                 |
| 86  | [What is Infrastructure Automation?](./devops-tools-and-automation/what-is-infrastructure-automation.md)                                                                      | 🟢 Beginner     |
| 87  | [What is GitOps?](./devops-tools-and-automation/what-is-gitops.md)                                                                                                            | 🟡 Intermediate |
| 88  | [What is ArgoCD?](./devops-tools-and-automation/what-is-argocd.md)                                                                                                            | 🟡 Intermediate |
| 89  | [What is Tekton?](./devops-tools-and-automation/what-is-tekton.md)                                                                                                            | 🟡 Intermediate |
| 90  | [What are Deployment Strategies?](./devops-tools-and-automation/what-are-deployment-strategies.md)                                                                            | 🟡 Intermediate |
|     | **[Cloud Cost Optimization](./cloud-cost-optimization/README.md)** (5)                                                                                                        |                 |
| 91  | [What is Cloud Cost Optimization?](./cloud-cost-optimization/what-is-cloud-cost-optimization.md)                                                                              | 🟢 Beginner     |
| 92  | [What are Reserved Instances?](./cloud-cost-optimization/what-are-reserved-instances.md)                                                                                      | 🟢 Beginner     |
| 93  | [What is Spot Instance pricing?](./cloud-cost-optimization/what-is-spot-instance-pricing.md)                                                                                  | 🟡 Intermediate |
| 94  | [How to implement cost tagging strategy?](./cloud-cost-optimization/how-to-implement-cost-tagging-strategy.md)                                                                | 🟡 Intermediate |
| 95  | [What are cost allocation reports?](./cloud-cost-optimization/what-are-cost-allocation-reports.md)                                                                            | 🟡 Intermediate |
|     | **[Site Reliability Engineering (SRE)](./site-reliability-engineering/README.md)** (9)                                                                                        |                 |
| 96  | [What is Site Reliability Engineering?](./site-reliability-engineering/what-is-site-reliability-engineering.md)                                                               | 🟢 Beginner     |
| 97  | [What are Service Level Objectives (SLOs)?](./site-reliability-engineering/what-are-service-level-objectives-slos.md)                                                         | 🟡 Intermediate |
| 98  | [What are Service Level Indicators (SLIs)?](./site-reliability-engineering/what-are-service-level-indicators-slis.md)                                                         | 🟡 Intermediate |
| 99  | [What is Error Budget?](./site-reliability-engineering/what-is-error-budget.md)                                                                                               | 🟡 Intermediate |
| 100 | [What is Toil in SRE?](./site-reliability-engineering/what-is-toil-in-sre.md)                                                                                                 | 🟡 Intermediate |
| 230 | [How do you do capacity planning?](./site-reliability-engineering/how-do-you-do-capacity-planning.md)                                                                         | 🔴 Advanced     |
| 231 | [What is a production readiness review?](./site-reliability-engineering/what-is-a-production-readiness-review.md)                                                             | 🟡 Intermediate |
| 232 | [What is the difference between SRE, DevOps, and Platform Engineering?](./site-reliability-engineering/what-is-the-difference-between-sre-devops-and-platform-engineering.md) | 🟡 Intermediate |
| 233 | [How do you design alerts that page a human?](./site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md)                                                   | 🔴 Advanced     |
|     | **[DevOps Metrics and KPIs](./devops-metrics-and-kpis/README.md)** (5)                                                                                                        |                 |
| 101 | [What are DevOps Metrics?](./devops-metrics-and-kpis/what-are-devops-metrics.md)                                                                                              | 🟢 Beginner     |
| 102 | [What is Mean Time to Recovery (MTTR)?](./devops-metrics-and-kpis/what-is-mean-time-to-recovery-mttr.md)                                                                      | 🟢 Beginner     |
| 103 | [What is Change Failure Rate?](./devops-metrics-and-kpis/what-is-change-failure-rate.md)                                                                                      | 🟡 Intermediate |
| 104 | [What is Deployment Frequency?](./devops-metrics-and-kpis/what-is-deployment-frequency.md)                                                                                    | 🟢 Beginner     |
| 105 | [What is Lead Time for Changes?](./devops-metrics-and-kpis/what-is-lead-time-for-changes.md)                                                                                  | 🟡 Intermediate |
|     | **[Serverless Architecture](./serverless-architecture/README.md)** (5)                                                                                                        |                 |
| 106 | [What is Serverless Computing?](./serverless-architecture/what-is-serverless-computing.md)                                                                                    | 🟢 Beginner     |
| 107 | [What is AWS Lambda?](./serverless-architecture/what-is-aws-lambda.md)                                                                                                        | 🟢 Beginner     |
| 108 | [What are the benefits of Serverless?](./serverless-architecture/what-are-the-benefits-of-serverless.md)                                                                      | 🟢 Beginner     |
| 109 | [What are Serverless Best Practices?](./serverless-architecture/what-are-serverless-best-practices.md)                                                                        | 🟡 Intermediate |
| 110 | [What is Function as a Service (FaaS)?](./serverless-architecture/what-is-function-as-a-service-faas.md)                                                                      | 🟢 Beginner     |
|     | **[Database Management in DevOps](./database-management-in-devops/README.md)** (5)                                                                                            |                 |
| 111 | [What is Database DevOps?](./database-management-in-devops/what-is-database-devops.md)                                                                                        | 🟡 Intermediate |
| 112 | [What is Database Version Control?](./database-management-in-devops/what-is-database-version-control.md)                                                                      | 🟡 Intermediate |
| 113 | [What are Database Migration Tools?](./database-management-in-devops/what-are-database-migration-tools.md)                                                                    | 🟡 Intermediate |
| 114 | [What is Database Backup Strategy?](./database-management-in-devops/what-is-database-backup-strategy.md)                                                                      | 🟡 Intermediate |
| 115 | [What is Database Performance Tuning?](./database-management-in-devops/what-is-database-performance-tuning.md)                                                                | 🔴 Advanced     |
|     | **[Network Security](./network-security/README.md)** (5)                                                                                                                      |                 |
| 116 | [What is Network Security in DevOps?](./network-security/what-is-network-security-in-devops.md)                                                                               | 🟡 Intermediate |
| 117 | [What is Zero Trust Security?](./network-security/what-is-zero-trust-security.md)                                                                                             | 🟡 Intermediate |
| 118 | [What is SSL/TLS?](./network-security/what-is-ssl-tls.md)                                                                                                                     | 🟢 Beginner     |
| 119 | [What is a Web Application Firewall (WAF)?](./network-security/what-is-a-web-application-firewall-waf.md)                                                                     | 🟢 Beginner     |
| 120 | [What is Network Segmentation?](./network-security/what-is-network-segmentation.md)                                                                                           | 🟡 Intermediate |
|     | **[Incident Management](./incident-management/README.md)** (5)                                                                                                                |                 |
| 121 | [What is Incident Management?](./incident-management/what-is-incident-management.md)                                                                                          | 🟢 Beginner     |
| 122 | [What is an Incident Response Plan?](./incident-management/what-is-an-incident-response-plan.md)                                                                              | 🟡 Intermediate |
| 123 | [What is Post-Mortem Analysis?](./incident-management/what-is-post-mortem-analysis.md)                                                                                        | 🟡 Intermediate |
| 124 | [What are Incident Severity Levels?](./incident-management/what-are-incident-severity-levels.md)                                                                              | 🟢 Beginner     |
| 125 | [What is On-Call Management?](./incident-management/what-is-on-call-management.md)                                                                                            | 🟡 Intermediate |
|     | **[DevOps Culture and Practices](./devops-culture-and-practices/README.md)** (5)                                                                                              |                 |
| 126 | [What is DevOps Culture?](./devops-culture-and-practices/what-is-devops-culture.md)                                                                                           | 🟢 Beginner     |
| 127 | [What are DevOps Best Practices?](./devops-culture-and-practices/what-are-devops-best-practices.md)                                                                           | 🟢 Beginner     |
| 128 | [What is Blameless Culture?](./devops-culture-and-practices/what-is-blameless-culture.md)                                                                                     | 🟡 Intermediate |
| 129 | [What is Knowledge Sharing in DevOps?](./devops-culture-and-practices/what-is-knowledge-sharing-in-devops.md)                                                                 | 🟢 Beginner     |
| 130 | [What is Team Collaboration in DevOps?](./devops-culture-and-practices/what-is-team-collaboration-in-devops.md)                                                               | 🟢 Beginner     |
|     | **[Infrastructure Monitoring](./infrastructure-monitoring/README.md)** (5)                                                                                                    |                 |
| 131 | [What is Infrastructure Monitoring?](./infrastructure-monitoring/what-is-infrastructure-monitoring.md)                                                                        | 🟢 Beginner     |
| 132 | [What are Monitoring Tools?](./infrastructure-monitoring/what-are-monitoring-tools.md)                                                                                        | 🟢 Beginner     |
| 133 | [What are Monitoring Best Practices?](./infrastructure-monitoring/what-are-monitoring-best-practices.md)                                                                      | 🟡 Intermediate |
| 134 | [What is Application Performance Monitoring?](./infrastructure-monitoring/what-is-application-performance-monitoring.md)                                                      | 🟡 Intermediate |
| 135 | [What is Log Management?](./infrastructure-monitoring/what-is-log-management.md)                                                                                              | 🟡 Intermediate |
|     | **[Cloud Migration](./cloud-migration/README.md)** (5)                                                                                                                        |                 |
| 136 | [What is Cloud Migration?](./cloud-migration/what-is-cloud-migration.md)                                                                                                      | 🟢 Beginner     |
| 137 | [What are Cloud Migration Strategies?](./cloud-migration/what-are-cloud-migration-strategies.md)                                                                              | 🟡 Intermediate |
| 138 | [What is Cloud Assessment?](./cloud-migration/what-is-cloud-assessment.md)                                                                                                    | 🟡 Intermediate |
| 139 | [What is Application Modernization?](./cloud-migration/what-is-application-modernization.md)                                                                                  | 🟡 Intermediate |
| 140 | [What are Cloud Migration Tools?](./cloud-migration/what-are-cloud-migration-tools.md)                                                                                        | 🟡 Intermediate |
|     | **[Advanced DevOps & Cloud](./advanced-devops-cloud/README.md)** (20)                                                                                                         |                 |
| 141 | [What is Platform Engineering?](./advanced-devops-cloud/what-is-platform-engineering.md)                                                                                      | 🔴 Advanced     |
| 142 | [What is FinOps?](./advanced-devops-cloud/what-is-finops.md)                                                                                                                  | 🟡 Intermediate |
| 143 | [What is Policy as Code?](./advanced-devops-cloud/what-is-policy-as-code.md)                                                                                                  | 🔴 Advanced     |
| 144 | [What is Chaos Engineering?](./advanced-devops-cloud/what-is-chaos-engineering.md)                                                                                            | 🔴 Advanced     |
| 145 | [What is Blue/Green Deployment?](./advanced-devops-cloud/what-is-blue-green-deployment.md)                                                                                    | 🟡 Intermediate |
| 146 | [What is Feature Flagging?](./advanced-devops-cloud/what-is-feature-flagging.md)                                                                                              | 🟡 Intermediate |
| 147 | [What is a Service Catalog?](./advanced-devops-cloud/what-is-a-service-catalog.md)                                                                                            | 🟡 Intermediate |
| 148 | [What is a Service Level Agreement (SLA)?](./advanced-devops-cloud/what-is-a-service-level-agreement-sla.md)                                                                  | 🟢 Beginner     |
| 149 | [What is a Service Level Objective (SLO)?](./advanced-devops-cloud/what-is-a-service-level-objective-slo.md)                                                                  | 🟢 Beginner     |
| 150 | [What is a Service Level Indicator (SLI)?](./advanced-devops-cloud/what-is-a-service-level-indicator-sli.md)                                                                  | 🟢 Beginner     |
| 151 | [What is a Runbook?](./advanced-devops-cloud/what-is-a-runbook.md)                                                                                                            | 🟢 Beginner     |
| 152 | [What is a Playbook in Incident Response?](./advanced-devops-cloud/what-is-a-playbook-in-incident-response.md)                                                                | 🟡 Intermediate |
| 153 | [What is Observability?](./advanced-devops-cloud/what-is-observability.md)                                                                                                    | 🔴 Advanced     |
| 154 | [What is Tracing in Observability?](./advanced-devops-cloud/what-is-tracing-in-observability.md)                                                                              | 🟡 Intermediate |
| 155 | [What is a Sidecar Pattern?](./advanced-devops-cloud/what-is-a-sidecar-pattern.md)                                                                                            | 🟡 Intermediate |
| 156 | [What is a Service Mesh Control Plane?](./advanced-devops-cloud/what-is-a-service-mesh-control-plane.md)                                                                      | 🔴 Advanced     |
| 157 | [What is GitHub Actions?](./advanced-devops-cloud/what-is-github-actions.md)                                                                                                  | 🟢 Beginner     |
| 158 | [What is a Self-Healing System?](./advanced-devops-cloud/what-is-a-self-healing-system.md)                                                                                    | 🔴 Advanced     |
| 159 | [What is Canary Analysis?](./advanced-devops-cloud/what-is-canary-analysis.md)                                                                                                | 🔴 Advanced     |
| 160 | [What is Infrastructure Drift?](./advanced-devops-cloud/what-is-infrastructure-drift.md)                                                                                      | 🟡 Intermediate |
|     | **[DevSecOps](./devsecops/README.md)** (8)                                                                                                                                    |                 |
| 161 | [What does a DevSecOps pipeline look like end to end?](./devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)                                                    | 🟡 Intermediate |
| 162 | [What is the difference between SAST, DAST, IAST, and SCA?](./devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md)                                             | 🟡 Intermediate |
| 163 | [What is a Software Bill of Materials (SBOM)?](./devsecops/what-is-a-software-bill-of-materials-sbom.md)                                                                      | 🟡 Intermediate |
| 164 | [What is SLSA and how do you secure the software supply chain?](./devsecops/what-is-slsa-and-how-do-you-secure-the-software-supply-chain.md)                                  | 🔴 Advanced     |
| 165 | [How do you sign and verify container images?](./devsecops/how-do-you-sign-and-verify-container-images.md)                                                                    | 🟡 Intermediate |
| 166 | [How do you manage secrets in CI/CD pipelines?](./devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md)                                                                  | 🟡 Intermediate |
| 167 | [How do you scan Infrastructure as Code before it is applied?](./devsecops/how-do-you-scan-infrastructure-as-code-before-it-is-applied.md)                                    | 🟡 Intermediate |
| 168 | [How do you prioritise vulnerabilities without blocking delivery?](./devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md)                            | 🔴 Advanced     |
|     | **[SecOps and Threat Detection](./secops/README.md)** (8)                                                                                                                     |                 |
| 169 | [What does a Security Operations Center (SOC) do?](./secops/what-does-a-security-operations-center-soc-do.md)                                                                 | 🟢 Beginner     |
| 170 | [What is a SIEM and how do you make one useful?](./secops/what-is-a-siem-and-how-do-you-make-one-useful.md)                                                                   | 🟡 Intermediate |
| 171 | [What is detection engineering?](./secops/what-is-detection-engineering.md)                                                                                                   | 🔴 Advanced     |
| 172 | [What is the MITRE ATT&CK framework?](./secops/what-is-the-mitre-att-and-ck-framework.md)                                                                                     | 🟡 Intermediate |
| 173 | [What is threat hunting?](./secops/what-is-threat-hunting.md)                                                                                                                 | 🔴 Advanced     |
| 174 | [How do you run a security incident response?](./secops/how-do-you-run-a-security-incident-response.md)                                                                       | 🟡 Intermediate |
| 175 | [What is EDR and how does it differ from antivirus?](./secops/what-is-edr-and-how-does-it-differ-from-antivirus.md)                                                           | 🟢 Beginner     |
| 176 | [What is SOAR and what should you automate first?](./secops/what-is-soar-and-what-should-you-automate-first.md)                                                               | 🟡 Intermediate |
|     | **[SLO Engineering](./slo-engineering/README.md)** (7)                                                                                                                        |                 |
| 177 | [How do you choose an SLO target?](./slo-engineering/how-do-you-choose-an-slo-target.md)                                                                                      | 🟡 Intermediate |
| 178 | [What is multi-window multi-burn-rate alerting?](./slo-engineering/what-is-multi-window-multi-burn-rate-alerting.md)                                                          | 🔴 Advanced     |
| 179 | [How do you measure a latency SLI correctly?](./slo-engineering/how-do-you-measure-a-latency-sli-correctly.md)                                                                | 🔴 Advanced     |
| 180 | [What is an error budget policy?](./slo-engineering/what-is-an-error-budget-policy.md)                                                                                        | 🟡 Intermediate |
| 181 | [How do you define SLOs for batch and asynchronous workloads?](./slo-engineering/how-do-you-define-slos-for-batch-and-asynchronous-workloads.md)                              | 🔴 Advanced     |
| 182 | [How do you handle SLOs for dependencies you do not own?](./slo-engineering/how-do-you-handle-slos-for-dependencies-you-do-not-own.md)                                        | 🔴 Advanced     |
| 183 | [What tooling do you use to implement SLOs?](./slo-engineering/what-tooling-do-you-use-to-implement-slos.md)                                                                  | 🟡 Intermediate |
|     | **[SLA Management](./sla-management/README.md)** (7)                                                                                                                          |                 |
| 184 | [What is the difference between an SLA, an SLO, an SLI, and an OLA?](./sla-management/what-is-the-difference-between-an-sla-an-slo-an-sli-and-an-ola.md)                      | 🟢 Beginner     |
| 185 | [How do you calculate allowed downtime for an availability target?](./sla-management/how-do-you-calculate-allowed-downtime-for-an-availability-target.md)                     | 🟢 Beginner     |
| 186 | [How do you calculate composite availability across dependencies?](./sla-management/how-do-you-calculate-composite-availability-across-dependencies.md)                       | 🔴 Advanced     |
| 187 | [What belongs in a well-written SLA?](./sla-management/what-belongs-in-a-well-written-sla.md)                                                                                 | 🟡 Intermediate |
| 188 | [How do service credits work?](./sla-management/how-do-service-credits-work.md)                                                                                               | 🟡 Intermediate |
| 189 | [How do you report SLA compliance to customers?](./sla-management/how-do-you-report-sla-compliance-to-customers.md)                                                           | 🟡 Intermediate |
| 190 | [What do you do when you breach an SLA?](./sla-management/what-do-you-do-when-you-breach-an-sla.md)                                                                           | 🟡 Intermediate |
|     | **[AWS Engineering](./aws-engineering/README.md)** (8)                                                                                                                        |                 |
| 191 | [How do you design a production-ready VPC on AWS?](./aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md)                                                      | 🟡 Intermediate |
| 192 | [How does AWS IAM evaluate a request?](./aws-engineering/how-does-aws-iam-evaluate-a-request.md)                                                                              | 🔴 Advanced     |
| 193 | [What is the difference between ECS, EKS, and Fargate?](./aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)                                              | 🟡 Intermediate |
| 194 | [How do Auto Scaling groups and load balancers work together on AWS?](./aws-engineering/how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md)                | 🟡 Intermediate |
| 195 | [What are the S3 storage classes and when do you use each?](./aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md)                                    | 🟡 Intermediate |
| 196 | [How do you run a highly available database on AWS?](./aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md)                                                  | 🔴 Advanced     |
| 197 | [How do you structure a multi-account AWS organisation?](./aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md)                                          | 🔴 Advanced     |
| 198 | [When do you choose CloudFormation, CDK, or Terraform on AWS?](./aws-engineering/when-do-you-choose-cloudformation-cdk-or-terraform-on-aws.md)                                | 🟡 Intermediate |
|     | **[Azure Engineering](./azure-engineering/README.md)** (8)                                                                                                                    |                 |
| 199 | [How is the Azure resource hierarchy organised?](./azure-engineering/how-is-the-azure-resource-hierarchy-organised.md)                                                        | 🟢 Beginner     |
| 200 | [What is Microsoft Entra ID and how does Azure RBAC work?](./azure-engineering/what-is-microsoft-entra-id-and-how-does-azure-rbac-work.md)                                    | 🟡 Intermediate |
| 201 | [How do you design an Azure virtual network?](./azure-engineering/how-do-you-design-an-azure-virtual-network.md)                                                              | 🟡 Intermediate |
| 202 | [What is Azure Kubernetes Service (AKS)?](./azure-engineering/what-is-azure-kubernetes-service-aks.md)                                                                        | 🟡 Intermediate |
| 203 | [What is Bicep and how does it compare to ARM templates?](./azure-engineering/what-is-bicep-and-how-does-it-compare-to-arm-templates.md)                                      | 🟡 Intermediate |
| 204 | [What is Azure Policy and how do landing zones use it?](./azure-engineering/what-is-azure-policy-and-how-do-landing-zones-use-it.md)                                          | 🔴 Advanced     |
| 205 | [How do you monitor Azure with Azure Monitor and KQL?](./azure-engineering/how-do-you-monitor-azure-with-azure-monitor-and-kql.md)                                            | 🟡 Intermediate |
| 206 | [When do you choose App Service, Container Apps, or Azure Functions?](./azure-engineering/when-do-you-choose-app-service-container-apps-or-azure-functions.md)                | 🟡 Intermediate |
|     | **[GCP Engineering](./gcp-engineering/README.md)** (8)                                                                                                                        |                 |
| 207 | [How is the GCP resource hierarchy organised?](./gcp-engineering/how-is-the-gcp-resource-hierarchy-organised.md)                                                              | 🟢 Beginner     |
| 208 | [How does IAM work in Google Cloud?](./gcp-engineering/how-does-iam-work-in-google-cloud.md)                                                                                  | 🟡 Intermediate |
| 209 | [What makes a Google Cloud VPC different?](./gcp-engineering/what-makes-a-google-cloud-vpc-different.md)                                                                      | 🟡 Intermediate |
| 210 | [What is the difference between GKE Standard and GKE Autopilot?](./gcp-engineering/what-is-the-difference-between-gke-standard-and-gke-autopilot.md)                          | 🟡 Intermediate |
| 211 | [What is Cloud Run and when do you choose it?](./gcp-engineering/what-is-cloud-run-and-when-do-you-choose-it.md)                                                              | 🟡 Intermediate |
| 212 | [How do you monitor Google Cloud with the Cloud Operations Suite?](./gcp-engineering/how-do-you-monitor-google-cloud-with-the-cloud-operations-suite.md)                      | 🟡 Intermediate |
| 213 | [How do you manage Google Cloud infrastructure as code?](./gcp-engineering/how-do-you-manage-google-cloud-infrastructure-as-code.md)                                          | 🟡 Intermediate |
| 214 | [When do you use BigQuery, Cloud SQL, or Spanner?](./gcp-engineering/when-do-you-use-bigquery-cloud-sql-or-spanner.md)                                                        | 🟡 Intermediate |
|     | **[Cloud Engineering](./cloud-engineering/README.md)** (7)                                                                                                                    |                 |
| 215 | [What is a cloud landing zone?](./cloud-engineering/what-is-a-cloud-landing-zone.md)                                                                                          | 🟡 Intermediate |
| 216 | [How do you connect an on-premises network to the cloud?](./cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md)                                      | 🟡 Intermediate |
| 217 | [How do you design least-privilege identity in the cloud?](./cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md)                                    | 🔴 Advanced     |
| 218 | [How do you design for multi-region resilience?](./cloud-engineering/how-do-you-design-for-multi-region-resilience.md)                                                        | 🔴 Advanced     |
| 219 | [What are the real trade-offs of multi-cloud?](./cloud-engineering/what-are-the-real-trade-offs-of-multi-cloud.md)                                                            | 🔴 Advanced     |
| 220 | [How do you manage DNS and global traffic routing?](./cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md)                                                  | 🟡 Intermediate |
| 221 | [How do the core services of AWS, Azure, and GCP map to each other?](./cloud-engineering/how-do-the-core-services-of-aws-azure-and-gcp-map-to-each-other.md)                  | 🟢 Beginner     |
|     | **[Platform Engineering](./platform-engineering/README.md)** (8)                                                                                                              |                 |
| 222 | [What is an Internal Developer Platform (IDP)?](./platform-engineering/what-is-an-internal-developer-platform-idp.md)                                                         | 🟡 Intermediate |
| 223 | [What is a golden path?](./platform-engineering/what-is-a-golden-path.md)                                                                                                     | 🟡 Intermediate |
| 224 | [How do you treat a platform as a product?](./platform-engineering/how-do-you-treat-a-platform-as-a-product.md)                                                               | 🔴 Advanced     |
| 225 | [What is Backstage?](./platform-engineering/what-is-backstage.md)                                                                                                             | 🟡 Intermediate |
| 226 | [What is Crossplane and how does it compare to Terraform?](./platform-engineering/what-is-crossplane-and-how-does-it-compare-to-terraform.md)                                 | 🔴 Advanced     |
| 227 | [How do you provide self-service environments to developers?](./platform-engineering/how-do-you-provide-self-service-environments-to-developers.md)                           | 🔴 Advanced     |
| 228 | [How do you measure the success of a platform?](./platform-engineering/how-do-you-measure-the-success-of-a-platform.md)                                                       | 🟡 Intermediate |
| 229 | [How do you roll out breaking platform changes safely?](./platform-engineering/how-do-you-roll-out-breaking-platform-changes-safely.md)                                       | 🔴 Advanced     |

<!-- TOC:END -->

</details>

---

## Repository structure

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
│   └── topic_meta.json             # topic registry: order, description, study notes
└── .github/workflows/
    └── validate-and-format.yml     # runs validation + Prettier on every PR
```

Directories and filenames carry **no numeric prefixes** — they are pure slugs. Ordering comes from two places instead:

- **Topic order** — the `order` field in `scripts/topic_meta.json`, which is also the registry of which directories count as topics.
- **Question order** — the `id` field in each question's frontmatter, unique across the repository.

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

Both are stdlib-only Python 3.11+ — no dependencies to install. CI runs the same commands and fails the pull request on drift.

---

## Contributing

New questions, better answers, and corrections are all welcome. [CONTRIBUTING.md](./CONTRIBUTING.md) covers the file format, naming rules, and the local checks to run before opening a pull request.

## License

Released under the [MIT License](./LICENSE).
