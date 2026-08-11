---
title: "What SRE interview questions come up when the company is not named?"
id: 364
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - unattributed
  - kubernetes
  - monitoring-and-logging
  - site-reliability-engineering
  - cicd
  - configuration-management
---

# What SRE interview questions come up when the company is not named?

## Questions

From one reported SRE round whose submitter did not name the employer.

- **Which commands do you use for Kubernetes, Docker, and Ansible?**
- **Explain the Kubernetes structure, ConfigMaps, and the scheduler.**
- **How do you troubleshoot an `ImagePullBackOff` error?**
- **Explain how you install Prometheus and Grafana.**
- **How do you monitor CPU metrics in Grafana?**
- **Explain how you build a CI/CD pipeline.**
- **How do you grant access to a user?**

## Example

```text
Unattributed SRE round
7 questions

  Monitoring                  2   install Prometheus + Grafana,
                                  monitor CPU metrics in Grafana
  Kubernetes                  2   structure + ConfigMaps + scheduler,
                                  ImagePullBackOff triage
  Tooling commands            1   Kubernetes, Docker, and Ansible commands
  CI/CD                       1   how you build a pipeline
  Access control              1   granting a user access

A SHORT, OPEN-ENDED ROUND
  Seven questions, all "explain how you..." — so each answer carries about
  14% of the round. There is no way to score well with one-line answers;
  every question needs a mechanism and a decision you made.
```

## Interview tips

- `ImagePullBackOff` has a well-defined cause list and a diagnostic path, so give both. `kubectl describe pod` and read the events — the message tells you which failure it is. The causes: the image name or tag does not exist (a typo, or a tag deleted from the registry); the registry is private and there is no `imagePullSecret`, or the secret is in the wrong namespace, since secrets are namespaced; registry authentication has expired, which for ECR means the node or Pod identity lacks `ecr:GetAuthorizationToken`; the node cannot reach the registry at all because there is no NAT or VPC endpoint; the registry is rate-limiting, which is the classic Docker Hub anonymous-pull limit; or the platform architecture does not match, such as an `arm64` image on `amd64` nodes. Say that `ErrImagePull` is the first failure and `ImagePullBackOff` is the kubelet backing off after repeated attempts — that distinction shows you have read the events rather than memorised the symptom. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- "Monitor CPU metrics in Grafana" is a question where naming the actual query separates you from everyone else. Grafana does not collect anything — it queries Prometheus, and for container CPU the metric comes from cAdvisor via the kubelet: a `rate()` over `container_cpu_usage_seconds_total` because it is a counter, summed by Pod, and divided by the CPU request or limit to express utilisation. For host CPU it is node-exporter's `node_cpu_seconds_total` with the `idle` mode subtracted. Then add the SRE point that earns the round: raw CPU usage is a _saturation_ signal, and the more useful container metric is `container_cpu_cfs_throttled_seconds_total`, because a container throttled against its limit shows latency spikes while its CPU usage looks unremarkable. See [what Grafana is](../monitoring-and-logging/what-is-grafana.md) and [writing effective PromQL queries and Alertmanager rules](../monitoring-and-logging/how-do-you-write-effective-promql-queries-and-alertmanager-rules.md).
- For installing Prometheus and Grafana, do not describe downloading binaries. Say you deploy the `kube-prometheus-stack` Helm chart, which brings the Prometheus Operator, Prometheus, Alertmanager, Grafana, node-exporter as a DaemonSet, and kube-state-metrics — and then explain what each piece contributes: node-exporter for host metrics, kube-state-metrics for the desired state of Kubernetes objects, cAdvisor via the kubelet for container usage. Add the operational decisions that make it a real answer: persistent storage and retention for Prometheus, ServiceMonitor and PodMonitor objects so applications are discovered declaratively, dashboards provisioned as code rather than clicked together, and remote write or Thanos if you need long-term or cross-cluster query. See [what Prometheus is](../monitoring-and-logging/what-is-prometheus.md).
- The Kubernetes structure question bundles three things, so answer them as a chain rather than three definitions. Structure: control plane — API server as the only front door, etcd as the store, scheduler for placement, controller manager running reconciliation loops — and nodes running kubelet, kube-proxy, and a container runtime. Scheduler specifically: it watches for Pods with no `nodeName`, filters nodes that cannot run them (resource requests, selectors, taints, volume topology), scores the survivors, and binds the Pod to the winner — say that it uses _requests_, not actual usage. ConfigMaps: non-confidential key-value configuration injected as environment variables or mounted files, with the practical detail that a mounted ConfigMap updates in place while an environment variable does not, so a rolling restart is needed to pick up changes. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- The commands question is an invitation to sound fluent, so group them by intent rather than reciting. Kubernetes: `get`/`describe`/`logs --previous`/`exec`/`apply`/`rollout status`/`rollout undo`/`top`/`auth can-i`/`debug`. Docker: `build`/`run`/`ps`/`logs`/`exec`/`inspect`/`image prune`/`history`. Ansible: `ansible-playbook` with `--check`, `--diff`, `--limit`, `--tags`, `-vvv`, plus `ansible-vault` and ad-hoc `ansible all -m ping`. Then say which you reach for first when something is broken — `describe` for events, `logs --previous` for a crashed container — because the ordering is the real signal. See [basic Linux commands](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md).
- "How do you grant access to a user?" is deliberately ambiguous, and the strongest move is to answer it at both layers. Kubernetes: authenticate via OIDC or certificates rather than long-lived tokens, then a Role and RoleBinding in the namespaces they need — binding the built-in `view` or `edit` ClusterRole through a namespaced RoleBinding is the idiomatic way — verified with `kubectl auth can-i --as`. Cloud: federated SSO with permission sets or roles, never a long-lived access key, with MFA and permissions generated from observed activity. Say the principle once — least privilege, time-bound, auditable — and that you never grant `cluster-admin` to an individual. See [how RBAC works in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md) and [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- For "how you build a CI/CD pipeline", give one pipeline you actually own, stage by stage, and name the gates: build once and produce an immutable artefact tagged by Git SHA, run unit tests and static analysis, scan dependencies and the image, push to a registry, deploy to a lower environment automatically, then promote _the same artefact_ upward with an approval before production. Say that rebuilding per environment means you never tested what you shipped. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md) and [continuous delivery versus continuous deployment](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md).
- Nothing in this round asks about SLIs, SLOs, error budgets, or incident response — which is unusual for an SRE title and suggests a platform-operations role wearing an SRE label. Volunteer the reliability framing anyway where it fits naturally: when asked about monitoring, mention that you alert on user-facing symptoms and error-budget burn rather than raw CPU thresholds. It costs one sentence and reframes you as an SRE rather than an operator. See [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md) and [error budgets](../site-reliability-engineering/what-is-error-budget.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
