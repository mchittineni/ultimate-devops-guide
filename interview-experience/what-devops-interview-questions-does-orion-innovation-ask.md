---
title: "What DevOps interview questions does Orion Innovation ask?"
id: 362
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - orion-innovation
  - network-security
  - kubernetes
  - aws-engineering
  - azure-engineering
  - cicd
  - database-management-in-devops
---

# What DevOps interview questions does Orion Innovation ask?

## Questions

**DNS**

- **What is an A record and what does it do in DNS?**
- **What is the value of an A record?**
- **What is a CNAME record?**
- **What is an MX record?**

**Certificates and load balancing**

- **The Application Gateway TLS certificate has expired. What steps do you follow to renew it?**
- **Is Application Gateway a layer 7 or a layer 4 load balancer?**

**Kubernetes**

- **You have 10 worker nodes and need to deploy Tomcat as a Pod on each one. How do you achieve that?**
- **You have an Apache Tomcat application running in a Kubernetes cluster. Which manifest files would you have for it?**
- **You have a local laptop and want to reach your hosted website. Which Kubernetes service type would you use?**

**AWS networking and databases**

- **You have multiple VPCs. How do you connect them in AWS?**
- **There is an RDS instance in the India region and you want read synchronisation with an RDS in the London region. How do you implement that?**

**CI/CD secrets**

- **You want to store secrets for use in a Jenkins pipeline. How do you do it?**

## Example

```text
Orion Innovation — DevOps Engineer (5 YOE), reported round
12 questions

  DNS                         4   A record + its value, CNAME, MX
  Kubernetes                  3   Tomcat on all 10 nodes, manifest set
                                  for a Tomcat app, reach it from a laptop
  Certificates / LB           2   renew an expired App Gateway certificate,
                                  is App Gateway L7 or L4
  AWS networking / database   2   connect multiple VPCs, cross-region
                                  RDS read replication
  CI/CD secrets               1   secrets in a Jenkins pipeline

THE ONE-WORD ANSWER QUESTION
  "Tomcat on each of 10 nodes" has a single correct answer — DaemonSet — and
  the interviewer is checking whether you reach for it or start describing
  replica counts and node affinity.
```

## Interview tips

- The 10-nodes question has one right answer: a **DaemonSet**, which places exactly one Pod on every matching node and automatically adds one when a node joins the cluster. Say why the alternatives are wrong — a Deployment with `replicas: 10` gives you ten Pods that the scheduler may stack several to a node, and it will not follow node additions or removals. Add that node selectors and tolerations narrow which nodes the DaemonSet covers, and note in passing that Tomcat is an odd DaemonSet candidate in reality, since DaemonSets normally carry node-level agents. Naming the mismatch politely reads as judgement. See [DaemonSets](../container-orchestration-advanced/what-are-daemonsets-in-kubernetes.md).
- The laptop-access question is testing whether you know the exposure ladder, so give it in order and pick one: `kubectl port-forward` for quick local access with no infrastructure change; NodePort if you can reach the nodes directly; **LoadBalancer** for a real cloud-provisioned address, which is the answer for a hosted website; and an Ingress in front if you want one load balancer serving many hostnames and paths with TLS. Say that for a website you would use an Ingress behind a single LoadBalancer rather than a LoadBalancer per service, because that is the cost-and-manageability answer. See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md) and [what a Service is](../kubernetes/what-is-a-service-in-kubernetes.md).
- For the Tomcat manifest set, list them by role rather than at random: a Deployment for the application, a Service to give it a stable address, an Ingress for external routing with TLS, a ConfigMap for `server.xml` or environment configuration, a Secret for credentials and the keystore, a PVC if it needs persistent storage, an HPA for scaling, a ServiceAccount if it needs cloud permissions, and a PodDisruptionBudget so upgrades cannot drain it. Then mention liveness and readiness probes on the Tomcat health endpoint as the thing that actually makes deploys safe.
- Application Gateway is **layer 7** — it terminates HTTP and HTTPS, does host and path-based routing, hosts a WAF, rewrites headers, and handles cookie-based session affinity. Give the contrast so the answer is complete: Azure Load Balancer is the layer 4 product, and the AWS equivalents are ALB at layer 7 and NLB at layer 4. See [layer 4 versus layer 7 load balancers](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md).
- The expired-certificate question wants a procedure and then a prevention, and the prevention is where the marks are. Procedure: obtain or renew the certificate, upload it to Key Vault (or as a listener certificate), point the Application Gateway listener at the _versionless_ Key Vault secret identifier, verify the full chain and that the intermediate certificates are present, then test with `openssl s_client` or a browser and confirm no stale cached certificate on the gateway. Prevention: store the certificate in Key Vault with auto-rotation and reference it versionlessly, so a renewal is picked up without touching the gateway — a version-pinned reference is exactly why certificates "expire despite being renewed". Add expiry monitoring with an alert at 30 days. See [what SSL/TLS is](../network-security/what-is-ssl-tls.md).
- The cross-region RDS question has a specific answer: a **cross-region read replica**, which replicates asynchronously from the India primary to a readable replica in London and can be promoted to a standalone primary if needed. Say that replication is asynchronous so there is replica lag and therefore a non-zero RPO, that the source needs automated backups enabled with a retention period above zero, and that for Aurora you would instead use a global database, which gives sub-second replication and faster failover. Mention that read traffic in London should be pointed at the replica endpoint, not the primary, or the exercise has no benefit. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md) and [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md).
- Connecting multiple VPCs should be answered by scale, not by naming one product. For two or three VPCs, peering is simple and cheap but does not transit, so N VPCs need N(N-1)/2 connections. Beyond that, Transit Gateway is a regional hub with transitive routing and cross-account sharing. If you only need to expose one service rather than join networks, PrivateLink is the right answer and it works even with overlapping CIDRs — which peering cannot. Say that overlapping CIDR ranges are the constraint that usually decides this. See [structuring a multi-account AWS organisation](../aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md).
- The DNS block is four short questions, so answer them tightly and add the operational rules. An A record maps a hostname to an IPv4 address, and its value _is_ that address — with AAAA doing the same for IPv6. A CNAME aliases one name to another name, and the two rules that matter are that it cannot coexist with other records at the same name and cannot sit at a zone apex, which is why providers offer alias or ANAME records for the bare domain. An MX record routes mail for a domain to named mail servers, with a preference number where lower wins — and note that an MX value must be a hostname, never an IP address. That last detail is a good discriminator. See [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).
- Jenkins secrets should be answered as a hierarchy. Baseline: the Credentials plugin with folder-scoped credentials, consumed via `withCredentials` so values are masked in the log. Better: Jenkins fetches from an external store — Key Vault, Vault, or Secrets Manager — at run time, so nothing is stored on the controller. Best: no stored credential at all, using OIDC federation to the cloud provider for short-lived tokens. Then name the classic leak: interpolating a secret inside a double-quoted Groovy string puts it in the build log, so use single quotes and let the shell expand it. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md) and [preventing and handling secret leaks in CI/CD](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
