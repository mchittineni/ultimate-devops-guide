---
title: "What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?"
id: 710
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - devsecops
  - stride
  - threat-modeling
  - architecture
  - security
quiz:
  stem: "Under the STRIDE threat modeling framework, which security control directly mitigates 'Repudiation' threats (where a user claims they did not perform a fraudulent action)?"
  options:
    - "Adding a Web Application Firewall"
    - "Maintaining immutable, cryptographically verifiable audit logs with tamper-evident user identity tracking"
    - "Increasing database RAM capacity"
    - "Enabling multi-region active-active replication"
  answer: 2
  explanation: "Repudiation is the ability to deny performing an action. Comprehensive, tamper-evident audit logs and digital signatures prove non-repudiation."
---

# What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?

**Short answer:** Threat modeling identifies architectural security risks before writing code; the STRIDE framework evaluates six threat categories (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) across data flow diagrams.

## Detail

A design flaw found in production can need a re-architecture, a migration, and an incident; found on a whiteboard, it costs a conversation. Threat modelling is how you find it on the whiteboard. **PASTA** (Process for Attack Simulation and Threat Analysis) is the heavier alternative: seven stages from business objectives through attack simulation to risk-ranked countermeasures, worth it for high-value systems but too slow for every story.

### The STRIDE Framework

| Threat                     | Description                           | Countermeasure / Security Control                      |
| -------------------------- | ------------------------------------- | ------------------------------------------------------ |
| **Spoofing**               | Pretending to be someone else         | Strong authentication, mTLS, PKI, API keys             |
| **Tampering**              | Modifying data or code unauthorized   | Cryptographic hashing, signatures, TLS integrity       |
| **Repudiation**            | Claiming you didn't perform an action | Cryptographic immutable audit logs, digital signatures |
| **Information Disclosure** | Leaking sensitive data                | Encryption at rest and in transit, masking, DLP        |
| **Denial of Service**      | Exhausting system availability        | Rate limiting, circuit breakers, autoscaling, WAF      |
| **Elevation of Privilege** | Gaining unauthorized permissions      | Least privilege RBAC, unprivileged non-root containers |

### Practical Sprint Threat Modeling

During architectural sprint planning, engineers draw a **Data Flow Diagram (DFD)** and identify trust boundaries (e.g. crossing from public internet to internal VPC), applying STRIDE to each boundary before writing the first line of code.

## Example

```text
Feature: "users upload profile images to S3 via a presigned URL"

Trust boundary crossed      STRIDE threat                    Mitigation (becomes a story/AC)
--------------------------  -------------------------------  ---------------------------------------------
Browser -> API              S: forged session                OIDC auth, short-lived tokens
API -> S3 (presigned PUT)   T: oversized / non-image upload  content-length-range + content-type in policy
                            I: guessable object keys         random UUID keys, private bucket, no listing
S3 -> image worker          E: parser exploit (ImageTragick) sandboxed worker, no IAM beyond the bucket
All                         R: "I never uploaded that"       CloudTrail data events + app audit log
```

## Interview tips

- Anchor it on the four questions from the Threat Modeling Manifesto: _What are we working on? What can go wrong? What are we going to do about it? Did we do a good job?_ STRIDE is one way to answer the second.
- Contrast the frameworks: **STRIDE** is lightweight and developer-friendly (per element or per trust boundary on a DFD); **PASTA** is a seven-stage, risk- and business-impact-driven process suited to high-value systems; **LINDDUN** covers privacy threats. Choosing the right weight for the change is part of the answer.
- To make it fit sprints, scope it to the change: a 30-minute session when a story adds a trust boundary, new data store, or external integration, with every mitigation filed as a ticket or acceptance criterion. A threat model with no tickets changed nothing.
- Keep models as code or diagrams in the repo (for example OWASP Threat Dragon or pytm) so they are reviewed and updated with the architecture.
- Admit the limitation: threat modelling depends on people's imagination and an accurate diagram; it complements, rather than replaces, testing and runtime detection. Treat "100x cheaper" style figures as illustrative - the direction is right, the precise multiplier is folklore.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?]] (`#539`): [What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?](../cicd/what-are-slsa-supply-chain-levels-for-software-artifacts-frameworks-and-how-do-they-verify-build-integrity.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
