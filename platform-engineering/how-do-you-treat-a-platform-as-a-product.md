---
title: "How do you treat a platform as a product?"
id: 224
category: "Platform Engineering"
difficulty: "Advanced"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# How do you treat a platform as a product?

**Short answer:** Give it identified users, a roadmap driven by their problems, a versioned interface with deprecation policy, documentation and support channels, adoption metrics, and someone accountable for whether developers actually choose it. The concrete difference from a tools team is that success is measured by voluntary adoption and developer outcomes, not by tickets closed or components shipped.

## Detail

**Know your users and their jobs.** Application engineers, on-call responders, data teams, and security all consume the platform differently. Do the discovery work: shadow a team's first deployment, watch where they get stuck, count how often they ask the same question in Slack. Roadmaps built from a conference talk rather than from user research are the standard platform failure mode.

**Adoption is voluntary or the signal is worthless.** If teams are compelled to use the platform, you cannot tell whether it is good. Mandates hide problems; voluntary adoption forces the platform to be genuinely better than the alternative. Where a mandate exists for compliance reasons, invest even harder in listening, because the usual feedback channel is closed.

**Version the interface and deprecate on a published policy.** The platform's API - templates, CRDs, pipeline contracts, CLI - is a public interface with consumers. Semantic versioning, a stated support window, migration tooling for breaking changes, and a deprecation notice period. Breaking 40 teams' pipelines without notice destroys credibility permanently, and no amount of technical excellence recovers it.

**Support is part of the product.** A staffed channel with a response expectation, a rota so it is not always the same person, office hours, and a documentation set that is treated as a deliverable rather than an afterthought. Every repeated question is a defect in either documentation or design - track them and fix the cause.

**Measure outcomes, not activity.** Lead time from commit to production, change failure rate, time to first successful deploy for a new service, self-service completion rate versus tickets, number of teams on the current supported version, developer satisfaction from a short recurring survey, and platform cost per team. DORA metrics plus a developer-experience survey is the usual pairing; "components delivered" is the vanity metric to avoid.

**Team topology.** A platform team is a distinct type from a stream-aligned team: it owns a product, has a product manager or someone doing that job, and interacts with consumers through X-as-a-Service rather than by embedding. When adoption stalls, temporary enabling-team engagements - pairing with one team to migrate - usually beat writing more documentation.

## Example

```text
Platform quarterly review - the artefacts that make it a product

Users            42 services across 11 teams · 3 personas interviewed this quarter
Top user pain    1. staging environments take 3 days   (roadmap: ephemeral envs)
                 2. secret rotation is manual          (roadmap: rotation operator)
                 3. unclear how to debug a failed deploy (docs + CLI improvement)
Adoption         new services on golden path      31/34  (91%)
                 services on supported template   28/42  (67%, target 85%)
                 self-service completion          88% (12% needed platform help)
Outcomes         median commit -> prod            22 min (was 51 min)
                 change failure rate              9%     (was 14%)
                 developer satisfaction (CSAT)    4.1/5, n=37
Interface        platform.acme.com/v1 stable · v1beta1 deprecated, removal 2026-11-01
                 migration tool shipped; 9 of 14 consumers migrated
Cost             $/ team / month published so teams can see their own consumption
```

## Interview tips

- Lead with users, roadmap, versioned interface, and adoption metrics - that framing is the answer.
- "Voluntary adoption is the only honest signal" is a strong, opinionated line to deliver.
- Expect: "how do you measure success?" - DORA outcomes plus adoption and satisfaction, explicitly rejecting output metrics.

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
