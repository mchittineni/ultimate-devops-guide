---
title: "What is a golden path?"
id: 223
category: "Platform Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# What is a golden path?

**Short answer:** A golden path is the supported, opinionated route through the platform for a common task - creating a service, adding a database, shipping to production - where the default choices are already made, compliant, and maintained by the platform team. It is a recommendation made irresistible by being the easiest option, not a rule enforced by policy.

## Detail

**What a complete golden path includes:** a scaffolded repository with a working build, a pipeline that tests, scans, signs, and deploys; observability wired up (dashboards, alerts, an SLO); the ownership record in the catalogue; secrets and configuration patterns; and documentation that assumes nothing. Anything missing becomes the developer's problem and erodes trust in the path.

**Paths are per-use-case, not one grand template.** Typical set: HTTP service, event consumer, scheduled job, and data pipeline. Four well-maintained paths beat one configurable template with 40 flags, which nobody understands and the platform team cannot support.

**Maintained means versioned.** Scaffolding that is copied once and diverges immediately provides value only on day one. The stronger pattern keeps the generated repository linked to a template version so updates can be pushed as pull requests - a base image bump, a new required security check - and adoption is measurable.

**Deviation is allowed and priced.** A team can leave the path when they have a real need; they then own what the platform was handling. Make that trade explicit ("off-path services do not get the platform SLO, automated compliance evidence, or upgrade support"), and track how many services are off-path - a rising number is feedback that the path is missing something.

**Measure adoption honestly.** Percentage of new services created via the path, time from repository creation to first production deploy, and the share of services still on a supported template version. If teams route around the path, the diagnosis is that it is too rigid or too incomplete, not that they are undisciplined.

**Balance opinion against escape hatches.** Strong opinions where variation adds no value (logging format, base images, deployment mechanics, tagging), flexibility where it does (language, data model, internal architecture). Getting that split wrong in either direction is how platforms fail: too rigid and teams leave, too flexible and it provides nothing.

## Example

```bash
# The whole golden path, from the developer's point of view
$ acme new service checkout --template http-service --owner team-payments
  ✔ repository created from template http-service@2.4.0
  ✔ CI pipeline: test, SAST, SCA, image build + sign, SBOM attestation
  ✔ dev + staging namespaces, ingress, secrets via workload identity
  ✔ dashboard, alerts, and a 99.9% availability SLO with burn-rate paging
  ✔ registered in the catalogue; on-call rotation linked
  ✔ pull request opened with a walkthrough of what was generated

  Production deploy: merge to main after review. Estimated first deploy: 25 minutes.
  Off-path? You own CI, observability, and compliance evidence yourself.
```

```yaml
# Template version tracked in the repo so updates arrive as pull requests
.acme/template.yaml:
  template: http-service
  version: 2.4.0
  upgrades: auto-pr # platform opens PRs for template changes
```

## Interview tips

- Emphasise "easiest path, not mandated path" - mandate-first answers signal a platform teams resent.
- The versioned-template-with-auto-PR detail is what distinguishes a maintained path from a one-time generator.
- Expect: "what if a team wants something different?" - allow it, make the trade explicit, and treat the deviation as product feedback.

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
