---
title: "What is the NIST Cybersecurity Framework (CSF) 2.0 and how is it used?"
id: 767
category: "Security and Compliance"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - security-and-compliance
  - nist
  - governance
  - compliance
quiz:
  stem: "Which function did NIST CSF 2.0 add to the five functions of CSF 1.1?"
  options:
    - "Deploy"
    - "Govern - covering risk strategy, roles and responsibilities, policy, oversight, and cybersecurity supply chain risk management"
    - "Encrypt"
    - "Audit"
  answer: 2
  explanation: "CSF 2.0 (February 2024) added Govern to Identify, Protect, Detect, Respond, and Recover, making governance and supply-chain risk explicit and placing it at the centre of the framework."
---

# What is the NIST Cybersecurity Framework (CSF) 2.0 and how is it used?

**Short answer:** The NIST CSF is a voluntary, outcome-based framework for managing cybersecurity risk, published as **version 2.0 in February 2024**. It organises outcomes into six **Functions** - **Govern, Identify, Protect, Detect, Respond, Recover** - broken into Categories and Subcategories (for example `PR.AA` identity management and access control). Organisations use it by writing a **Current Profile** (where we are), a **Target Profile** (where we need to be, given our risk), and a prioritised plan to close the gap, with **Tiers** describing how rigorous their risk practices are. It is not a certification and not a control catalogue: it says _what_ outcomes to achieve and points, through Informative References, to catalogues such as NIST SP 800-53, ISO/IEC 27001, and the CIS Controls for _how_.

## Detail

### What changed in 2.0

- **Govern** is new and sits at the centre: risk strategy, roles and accountability, policy, oversight, and **cybersecurity supply chain risk management** (GV.SC). It reflects that most failures are governance failures, not missing tools.
- **Scope broadened** from "critical infrastructure" to every organisation, of any size or sector.
- **Implementation Examples and Quick-Start Guides** make Subcategories concrete, and the reference material moved online (the CSF 2.0 Reference Tool) so mappings can be updated without a new version.
- **Community Profiles** let sectors publish shared Target Profiles, and the framework links explicitly to NIST's privacy framework and enterprise risk management guidance.

### The six Functions

| Function     | Outcome                                                    | DevOps-relevant examples                                             |
| ------------ | ---------------------------------------------------------- | -------------------------------------------------------------------- |
| **Govern**   | Risk strategy, roles, policy, oversight, supply chain risk | Ownership of each control, vendor and open-source dependency policy  |
| **Identify** | Know assets, risks, and improvement opportunities          | Asset and SBOM inventory, threat modelling, vulnerability management |
| **Protect**  | Safeguards to manage risk                                  | SSO and MFA, least privilege, encryption, secure SDLC, hardening     |
| **Detect**   | Find and analyse attacks and anomalies                     | SIEM, EDR, cloud audit logs, detection engineering                   |
| **Respond**  | Act on detected incidents                                  | Incident response plan, triage, containment, communication           |
| **Recover**  | Restore assets and operations                              | Backups tested by restore, DR runbooks, post-incident improvement    |

### How it is used in practice

1. **Scope** the organisation or system and its risk appetite (Govern).
2. **Assess the Current Profile**: for each relevant Subcategory, how well is the outcome achieved today, with evidence.
3. **Define the Target Profile**, often starting from a Community Profile for your sector, and prioritised by business risk rather than "everything to maximum".
4. **Gap analysis and plan**: owners, dates, budget; track it like any roadmap.
5. **Measure and repeat**: re-assess on a cadence and after major incidents or changes.

**Tiers** (Partial, Risk Informed, Repeatable, Adaptive) describe the rigour of governance and risk management. They are not maturity scores for individual controls, and the target is not automatically Tier 4.

### How it relates to other frameworks

- **ISO/IEC 27001** is a certifiable management-system standard with an audit; **SOC 2** is an attestation report by a CPA firm; **PCI DSS** is a mandatory standard for card data. CSF is none of these - it is a common language that maps onto all of them.
- **NIST SP 800-53** is the detailed control catalogue (mandatory for US federal systems); CSF is the outcome layer above it.
- **NIST SP 800-61 Rev. 3** (2025) organises incident response around the CSF 2.0 Functions, which is why IR plans increasingly use the same vocabulary.

A common pattern: use CSF to structure the programme and report to the board, ISO 27001 or SOC 2 for external assurance, and the CIS Controls or 800-53 for the technical baseline - with one internal control set mapped to all of them.

## Example

```text
Excerpt from a Current vs Target Profile for a SaaS platform team

Subcategory  Outcome (abridged)                                 Current            Target   Gap action (owner, due)
GV.SC-07     Supplier risks identified and monitored            Ad hoc reviews     Managed  SBOM + Renovate policy for all repos (platform, Q1)
ID.AM-02     Software and services inventoried                  Partial            Full     Generate SBOMs at build, store by digest (CI team, Q1)
PR.AA-05     Access permissions follow least privilege          Standing admin     JIT      IAM Identity Center + PIM, remove IAM users (IAM, Q2)
DE.CM-09     Computing hardware/software monitored              Hosts only         + K8s    Falco + K8s audit logs to SIEM (SecOps, Q2)
RS.MA-01     Incident response plan executed with stakeholders  Untested           Tested   Twice-yearly tabletop incl. legal and comms (CISO, Q3)
RC.RP-03     Backup integrity verified before restore           Never verified     Monthly  Automated restore test of prod DB snapshot (DBA, Q1)
```

```yaml
# Tag detections and controls with CSF Subcategories so coverage reports roll up automatically
- control: falco-shell-in-container
  csf: [DE.CM-09, DE.AE-02]
  attack: [T1059]
  evidence: siem://saved-search/falco-shell-alerts
- control: backup-restore-test
  csf: [RC.RP-03, PR.DS-11]
  evidence: s3://acme-audit-evidence/restore-tests/
```

## Interview tips

- Give the six Functions in order and say what 2.0 added: **Govern**, including supply chain risk management, at the centre of the model.
- Explain the mechanics - Functions, Categories, Subcategories; Current and Target Profiles; Tiers - and that the gap between the Profiles is the work plan.
- Be precise about what it is not: not a certification, not mandatory for most private companies, and not a control catalogue. It maps to ISO 27001, SOC 2, CIS Controls, and SP 800-53 through Informative References.
- Show how a DevOps team contributes evidence: inventories and SBOMs for Identify, IAM and secure pipelines for Protect, logs and detections for Detect, tested runbooks and restores for Respond and Recover.
- Say that Tiers describe the rigour of risk management and that not everything should target Tier 4 - prioritising by risk is the point.
- Mention SP 800-61 Rev. 3 now using CSF 2.0 for incident response, which shows you know how the NIST documents fit together. See [SOC 2, ISO 27001, and HIPAA](./what-are-soc-2-iso-27001-and-hipaa-compliance-frameworks-and-how-is-compliance-as-code-implemented.md) and [how do you automate compliance checks](./how-do-you-automate-compliance-checks-for-pci-dss-soc-2-hipaa-and-gdpr.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Policy as Code and how do OPA Gatekeeper and Kyverno enforce cluster governance?]] (`#707`): [What is Policy as Code and how do OPA Gatekeeper and Kyverno enforce cluster governance?](../devsecops/what-is-policy-as-code-and-how-do-opa-gatekeeper-and-kyverno-enforce-cluster-governance.md)
- [[How do you manage TLS certificates in production?]] (`#491`): [How do you manage TLS certificates in production?](../network-security/how-do-you-manage-tls-certificates-in-production.md)
- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
