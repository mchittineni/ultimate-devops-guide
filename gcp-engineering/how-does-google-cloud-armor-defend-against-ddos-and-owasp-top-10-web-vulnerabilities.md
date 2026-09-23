---
title: "How Does Google Cloud Armor Defend Against DDoS and OWASP Top 10 Web Vulnerabilities?"
id: 747
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - gcp-engineering
  - cloud-armor
  - ddos
  - waf
  - security
quiz:
  stem: "Where does Google Cloud Armor filter incoming traffic and enforce WAF security rules?"
  options:
    - "Directly inside each container pod's Linux kernel network namespace."
    - "At the edge of Google's global network, inspecting and dropping malicious packets before they reach backend compute resources."
    - "In a centralized database cluster located exclusively in Iowa."
    - "Only during scheduled offline nightly maintenance scans."
  answer: 2
  explanation: "Cloud Armor operates at the edge of Google's global network in tandem with Cloud Load Balancing, filtering out malicious requests and mitigating DDoS attacks before traffic ever touches your backend servers."
---

# How Does Google Cloud Armor Defend Against DDoS and OWASP Top 10 Web Vulnerabilities?

**Short answer:** Google Cloud Armor operates at the edge of Google's global network alongside Cloud Load Balancing, mitigating massive volumetric Layer 3/4 DDoS attacks using Google's global scale, and defending against Layer 7 application attacks (SQLi, XSS, OWASP Top 10) through preconfigured WAF rules, rate limiting, and adaptive protection.

## Detail

### Edge Protection at Google Scale

Web applications face attacks ranging from multi-terabit volumetric DDoS floods to targeted application-layer exploits. Google Cloud Armor leverages the global scale and infrastructure that protects Google Search and YouTube.

### Multi-Layered Protection Architecture

1. **Infrastructure DDoS Defense (Layers 3 & 4)**:
   - Built into Google's front ends for the global external Application Load Balancer and proxy Network Load Balancers; always-on for those load balancers.
   - Anycast IP addresses route incoming packets to the nearest Google Edge Point of Presence (POP).
   - Volumetric SYN floods, UDP amplification, and NTP reflection attacks are absorbed across Google's global edge network without impacting backend VMs or GKE pods.
2. **Web Application Firewall (WAF) (Layer 7)**:
   - **Preconfigured WAF rules based on the OWASP ModSecurity Core Rule Set** (rule names such as `sqli-v33-stable` and `xss-v33-stable`, tunable by sensitivity level): mitigate common OWASP Top 10 attack classes, including:
     - SQL Injection (SQLi)
     - Cross-Site Scripting (XSS)
     - Remote Code Execution (RCE)
     - Local File Inclusion (LFI)
     - Protocol attacks (HTTP request smuggling)
3. **Advanced Rate Limiting**:
   - `throttle` or `rate_based_ban` actions keyed on IP, header, cookie, path, or other keys, which slow brute-force login attempts and scraping.
4. **Cloud Armor Adaptive Protection** (full alerting and suggested rules require the Cloud Armor Enterprise tier, formerly Managed Protection Plus):
   - Uses machine learning models trained on application traffic patterns to detect volumetric Layer 7 attacks in real time, alerting analysts and generating proposed custom mitigation rules automatically.

```text
[Public Internet Attack Traffic]
                 │
                 ▼
[Google Global Edge POP (Anycast)] ──► L3/L4 DDoS Absorbed at Edge
                 │
[Global external Application Load Balancer + Cloud Armor policy] ──► Blocks SQLi, XSS, bad IPs, rate abuse
                 │ (Clean Traffic)
                 │
                 ▼
[Backend Services: GKE / Cloud Run / Compute Engine]
```

### Real-World Production Scenario

An online ticket retailer experiences a sudden 200,000 req/sec HTTP flood during a high-profile concert sale. Cloud Armor Adaptive Protection flags the abnormal layer 7 spike, identifies common header anomalies from the botnet, and presents a one-click rule that immediately blocks the botnet requests at Google's edge, preserving system stability for legitimate ticket buyers.

## Example

```bash
# Security policy with a preconfigured SQLi rule (preview first), and a per-IP rate-based ban
gcloud compute security-policies create web-policy --description="edge WAF for checkout"

gcloud compute security-policies rules create 1000 --security-policy=web-policy \
  --expression="evaluatePreconfiguredWaf('sqli-v33-stable', {'sensitivity': 1})" \
  --action=deny-403 --preview

gcloud compute security-policies rules create 2000 --security-policy=web-policy \
  --src-ip-ranges="*" --action=rate-based-ban \
  --rate-limit-threshold-count=300 --rate-limit-threshold-interval-sec=60 \
  --ban-duration-sec=600 --conform-action=allow --exceed-action=deny-429 \
  --enforce-on-key=IP

# Attach it to the load balancer's backend service
gcloud compute backend-services update checkout-backend --global --security-policy=web-policy
```

## Interview tips

- Highlight that Cloud Armor runs at the edge of Google's network, dropping malicious requests before they consume backend load balancer or compute capacity.
- Mention Adaptive Protection: Google's ML-driven detection of Layer 7 anomalies that automatically suggests firewall rules.
- Note that Cloud Armor attaches to backend services of the load balancer: GKE via Gateway API policies or `BackendConfig` on Ingress, and Cloud Run via a serverless NEG behind the load balancer - it cannot protect a Cloud Run `run.app` URL directly, so restrict ingress to the load balancer.
- Trade-offs: WAF signatures produce false positives, so deploy rules in preview mode first, tune sensitivity levels, and exclude specific request fields; a WAF does not replace fixing the application vulnerability.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does Cloud IAM Role Federation differ from static Service Account keys?]] (`#546`): [How does Cloud IAM Role Federation differ from static Service Account keys?](../cloud-platforms/how-does-cloud-iam-role-federation-differ-from-static-service-account-keys.md)
- [[How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?]] (`#543`): [How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?](../cloud-platforms/how-does-the-cloud-shared-responsibility-model-divide-security-obligations-between-iaas-paas-and-saas.md)
- [[What is the difference between Mutating and Validating Admission Webhooks in Kubernetes?]] (`#524`): [What is the difference between Mutating and Validating Admission Webhooks in Kubernetes?](../kubernetes/what-is-the-difference-between-mutating-and-validating-admission-webhooks-in-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
