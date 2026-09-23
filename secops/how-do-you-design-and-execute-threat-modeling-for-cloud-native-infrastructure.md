---
title: "How Do You Design and Execute Threat Modeling for Cloud-Native Infrastructure?"
id: 713
category: "SecOps and Threat Detection"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - secops
  - threat-modeling
  - cloud-security
quiz:
  stem: "In cloud-native threat modeling, what is the primary risk associated with unrestricted pod access to the cloud instance metadata service (IMDS)?"
  options:
    - "The pod can consume all host memory by repeatedly querying CPU telemetry."
    - "An SSRF vulnerability in the workload could allow an attacker to retrieve node IAM credentials and assume broad cloud privileges."
    - "Access to IMDS forces Kubernetes nodes to automatically reboot without grace periods."
    - "The container runtime will fail its health checks due to packet drops on RFC 1918 subnets."
  answer: 2
  explanation: "If a pod can reach the instance metadata endpoint without restrictions (e.g., via SSRF), an attacker can extract temporary node credentials and move laterally across cloud provider APIs."
---

# How Do You Design and Execute Threat Modeling for Cloud-Native Infrastructure?

**Short answer:** Cloud-native threat modeling identifies potential adversaries, entry vectors, and abuse cases across infrastructure components using structured frameworks like STRIDE or PASTA. It maps control plane trust boundaries, container runtimes, IAM privileges, and network interconnects to prioritize mitigations based on impact and likelihood.

## Detail

### The Shift to Cloud-Native Threat Modeling

Traditional software threat modeling focused primarily on monolithic application inputs and operating system boundaries. Cloud-native architectures introduce transient infrastructure, microsegmentation, shared-responsibility cloud APIs, container orchestration, and third-party SaaS integrations.

### Structured Frameworks

- **STRIDE**: Analyzes Spoofing (Identity), Tampering (Data integrity), Repudiation (Audit logging), Information Disclosure (Confidentiality), Denial of Service (Availability), and Elevation of Privilege (Authorization).
- **PASTA (Process for Attack Simulation and Threat Analysis)**: A seven-stage risk-centric methodology aligning business objectives with technical vulnerabilities and adversary attack patterns.
- **MITRE ATT&CK (Containers and Cloud matrices)** and Microsoft's **Threat Matrix for Kubernetes**: Map real-world tactics, techniques, and procedures (TTPs) to cloud environments, which keeps a threat model grounded in what attackers actually do.

### Core Trust Boundaries in Kubernetes & Cloud

1. **Developer Workstation to CI/CD**: Compromise of code repositories or build agents leading to poisoned container images or stolen deployment secrets.
2. **Kube-API Server Control Plane**: Unauthorized access via misconfigured RBAC, exposed public endpoints, or leaked service account tokens.
3. **Container Runtime & Host Kernel**: Container breakout via privileged capabilities (`CAP_SYS_ADMIN`), kernel exploits, or writable `hostPath` mounts (for example the container runtime socket).
4. **Cloud Metadata APIs (`169.254.169.254`)**: SSRF vulnerabilities in workloads exploited to retrieve instance IAM credentials.
5. **Ingress and Service Mesh**: Unauthenticated inter-service communication or bypass of edge WAF protections.

### Threat Modeling Matrix Example

| Threat Category            | Cloud Asset        | Attack Vector                                          | Mitigation Control                                                                                   |
| :------------------------- | :----------------- | :----------------------------------------------------- | :--------------------------------------------------------------------------------------------------- |
| **Elevation of Privilege** | Pod ServiceAccount | Pod compromise allows querying Kubernetes API          | Set `automountServiceAccountToken: false` unless the Pod calls the API; enforce RBAC least-privilege |
| **Information Disclosure** | Cloud Metadata API | Workload SSRF queries `169.254.169.254`                | Enforce IMDSv2 with hop-limit 1 on AWS; apply Cilium/Calico network policies                         |
| **Tampering**              | Container Registry | Pushed image modified or untrusted base image deployed | Enforce Sigstore/Cosign image signing verified by Kyverno or OPA Gatekeeper                          |

### Real-World Production Scenario

A financial platform designs a customer document verification service on EKS. Threat modeling reveals that malicious uploads could trigger image parser buffer overflows resulting in container execution. The team mitigates this by running the parsing pod under a non-root UID, dropping all Linux capabilities, restricting outbound network traffic via Calico policy, and enforcing IMDSv2 to prevent IAM role theft.

## Example

```python
# Threat model as code with OWASP pytm: the diagram and the threats live in the repo
from pytm import TM, Actor, Boundary, Dataflow, Datastore, Process

tm = TM("Document verification service")
internet = Boundary("Internet")
cluster = Boundary("EKS cluster")

user = Actor("Customer", inBoundary=internet)
api = Process("upload-api", inBoundary=cluster)
parser = Process("image-parser", inBoundary=cluster)
bucket = Datastore("S3 documents bucket", isEncrypted=True)

Dataflow(user, api, "Upload document (HTTPS)", protocol="HTTPS", isEncrypted=True)
Dataflow(api, parser, "Parse job")
Dataflow(parser, bucket, "Store result")

tm.process()   # python3 tm.py --report / --dfd emits threats and a data-flow diagram
```

## Interview tips

- Anchor on the four questions: what are we building, what can go wrong, what will we do about it, did we do a good job? Then show the cloud-native trust boundaries - CI/CD, the Kubernetes API, the container/host kernel boundary, the metadata service, and east-west traffic.
- Pick the framework to fit the stakes: STRIDE per trust boundary for everyday design reviews, PASTA or attack trees for high-value systems, ATT&CK and the Kubernetes threat matrix to check realism.
- Prioritise by impact and likelihood, and turn every accepted mitigation into a tracked ticket or policy (admission rule, IAM condition, NetworkPolicy); a model with no enforced outputs has not changed the risk.
- Mention the shared-responsibility line: on managed Kubernetes the provider owns the control-plane hosts, but RBAC, admission policy, workload identity, and network policy are yours.
- Keep models current: re-run when a new trust boundary, data store, or external integration appears, ideally triggered from the design-review or PR process, and store them as code (Threat Dragon JSON or pytm) so changes are reviewable.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SecOps and Threat Detection](./README.md) · [All topics](../README.md)
