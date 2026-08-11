---
title: "What DevOps interview questions does OPT IT ask?"
id: 358
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - opt-it
  - kubernetes
  - infrastructure-as-code
  - docker
  - monitoring-and-logging
  - cicd
  - aws-engineering
---

# What DevOps interview questions does OPT IT ask?

## Questions

**Kubernetes and networking**

- **If the databases sit in private subnets, how do you deploy into Kubernetes so the workload can reach them?**
- **Have you written Kubernetes manifests, and which kinds have you written?**

**Provisioning practice**

- **What best practices do you follow when creating resources such as EC2, RDS, and MongoDB?**
- **Explain the workspace concept and the module concept in Terraform.**

**Monitoring**

- **Which monitoring tools have you used?**
- **Why do you use Prometheus, and where did you deploy it?**

**Containers and CI/CD**

- **How do you containerise your application?**
- **Write a Dockerfile for a Java application.**
- **Which tool have you used for CI/CD, and what type of pipeline have you worked on?**

**Project and team**

- **How many microservices are in your project? Name some of them, and say which ones you worked on.**
- **How many people are on your team?**
- **What did you learn at your previous company?**
- **Do you have any questions for us?**

## Example

```text
OPT IT — DevOps Engineer (2+ YOE), reported round
13 questions

  Project and team            4   microservice count + names, which you owned,
                                  team size, learning from previous company
  Containers and CI/CD        3   containerisation approach, Java Dockerfile,
                                  CI/CD tool + pipeline type
  Kubernetes                  2   private-subnet databases, manifest kinds
  Provisioning practice       2   EC2/RDS/MongoDB best practices,
                                  Terraform workspaces + modules
  Monitoring                  2   tools used, why Prometheus and where

A JUNIOR ROUND, BUT NOT A SOFT ONE
  At 2+ years the interviewer spends a third of the round establishing what
  you personally owned rather than what your team did. Vague answers about
  "we" are the failure mode here — name your microservices and your work.
```

```dockerfile
# The Java Dockerfile they ask you to write — multi-stage, non-root,
# JVM told about its container limits.
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src
COPY pom.xml .
RUN mvn -B dependency:go-offline        # cached unless pom.xml changes
COPY src ./src
RUN mvn -B -DskipTests package

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /src/target/*.jar app.jar
RUN addgroup -S app && adduser -S app -G app
USER app
EXPOSE 8080
ENTRYPOINT ["java","-XX:MaxRAMPercentage=75","-jar","/app/app.jar"]
```

## Interview tips

- The private-subnet database question is the only real architecture question in the round, so give it weight. The answer is that the Kubernetes nodes or Pods must have a network path and permission: put the worker nodes in private subnets in the same VPC (or a peered one) so routing is local, allow the database's security group to accept traffic _from the node or Pod security group_ rather than from a CIDR, resolve the endpoint via private DNS, and use a Kubernetes Service of type `ExternalName` or just the RDS endpoint in a ConfigMap. Say explicitly that the database never needs a public IP and the application never needs internet egress to reach it. Add IRSA or Pod Identity if credentials come from Secrets Manager. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- On the Java Dockerfile, the details that separate a good answer are all about the JVM in a container. Use a multi-stage build so Maven and the JDK never ship; copy `pom.xml` and resolve dependencies _before_ copying source so the dependency layer caches; run as a non-root user; and set `-XX:MaxRAMPercentage` so the JVM sizes its heap from the container's cgroup limit rather than the host's memory — without that, a JVM in a memory-limited container is the classic `OOMKilled` cause. Saying that last point unprompted is the strongest thing you can do here. See [what a Dockerfile is](../docker/what-is-dockerfile.md) and [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- "Which manifest kinds have you written?" is a breadth check with an easy win: list them grouped by purpose — Deployment, StatefulSet, DaemonSet, Job and CronJob for workloads; Service, Ingress, and NetworkPolicy for networking; ConfigMap and Secret for configuration; PVC and StorageClass for storage; ServiceAccount, Role, and RoleBinding for access; HPA and PodDisruptionBudget for operations. Then say which you write most often and why. Grouping them sounds like understanding; a random list sounds like recall.
- The Terraform workspaces-and-modules question should come with an opinion, not just definitions. A module is a reusable, versioned package of resources with inputs and outputs, used so environments differ only in values. A workspace gives you multiple state files from one configuration — convenient when infrastructure is identical and only variables differ, but most teams prefer separate directories and state per environment because a workspace hides which environment you are targeting and makes it easy to apply to the wrong one. Say that trade-off. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md) and [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- For provisioning best practices across EC2, RDS, and MongoDB, answer with properties rather than a per-service list: everything through infrastructure as code and never by hand, private subnets by default with no public IPs, encryption at rest and in transit, IAM roles rather than stored credentials, mandatory tags for owner and environment, backups with a tested restore, multi-AZ for anything stateful, right-sized instances from observed usage, and least-privilege security groups referencing other groups rather than CIDRs. Say that the tagging and backup-restore points are the ones people skip.
- "Why Prometheus and where did you deploy it?" wants a reason and a topology. The reason: it is a pull-based, label-oriented time-series database with service discovery that fits ephemeral Kubernetes workloads, plus PromQL and Alertmanager. The topology: in-cluster via the kube-prometheus-stack Helm chart or the Prometheus Operator, with node-exporter as a DaemonSet, kube-state-metrics for object state, and remote write or Thanos if you need long retention. Naming the operator and the two exporters is what shows you deployed it rather than used it. See [what Prometheus is](../monitoring-and-logging/what-is-prometheus.md) and [what Grafana is](../monitoring-and-logging/what-is-grafana.md).
- Four questions probe what _you_ did — microservice names, which ones you owned, team size, what you learned. At 2 to 3 years these decide the round, because the interviewer is calibrating whether your experience is real. Prepare concrete numbers and names, and describe one thing you owned end to end. Vague or "we" answers read as inflated experience.
- "What did you learn at your previous company?" should not be a list of tools. Pick one habit or judgement you gained — reading logs before changing anything, writing the runbook before the automation, insisting on a rollback plan — and give the incident that taught it.
- The round ends with "any questions", which is scored even though it feels like a formality. Ask something that only someone who has done the work would ask: how deployments reach production, who is on call, what the biggest source of toil is. See [what questions you should ask your interviewer](./what-questions-should-you-ask-your-interviewer.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
