---
title: "How do you scale DevOps culture across many teams?"
id: 287
category: "DevOps Culture and Practices"
difficulty: "Advanced"
tags:
  - devops
  - devops-culture-and-practices
  - interview-questions
---

# How do you scale DevOps culture across many teams?

**Short answer:** You cannot mandate culture, so you change what is easy and what is measured. Make the good path the cheapest path (a paved road every team can adopt in a day), publish outcome metrics per team without turning them into a league table, move practices between teams through embedded engineers and communities of practice rather than documents, and let teams own the consequences of their own services. Culture follows incentives and feedback loops - not slide decks or a renamed operations team.

## Detail

**Why the usual attempts fail.** A central "DevOps team" becomes a new silo and a new ticket queue. A mandate ("all teams will practise trunk-based development by Q3") produces compliance theatre. Training alone does not survive contact with a delivery deadline. And a maturity-model spreadsheet measures adherence to a process rather than the outcome you actually want.

**The four levers that do work:**

**1. Make the good path the easy path.** Most teams do the wrong thing because the right thing costs three weeks of setup. A paved road - a service template with CI, observability, secret management, and progressive delivery wired in; a working pipeline in an hour; a golden path documented as a tutorial - converts a culture problem into an adoption problem, which is tractable. Crucially the paved road must be **optional but overwhelmingly attractive**: teams that leave it should be able to, and should then own the extra work themselves.

**2. Measure outcomes, per team, visibly.** DORA metrics plus operational load (pages per week, toil hours) per team, published where engineers already look. The rules that keep this healthy: never compare teams with different risk profiles as if they were the same; never attach the numbers to performance reviews (that is how you get gamed metrics); always pair a throughput metric with a stability metric so nobody optimises one by destroying the other. The purpose is to let a team see its own trend and ask for help.

**3. Move practice through people.** Written standards transfer information; people transfer practice. What works: an **enabling team** that embeds with one product team for a few weeks and leaves capability behind rather than artifacts; internal **communities of practice** with a real agenda; **guilds** owning a shared standard; **internal open source** with a CODEOWNERS-based review model so improvements flow between teams; and blameless incident reviews published organisation-wide so one team's outage teaches forty.

**4. Give teams the consequences.** "You build it, you run it" is the mechanism, not the slogan: the team that ships owns the pager for what it shipped. Nothing improves test quality and observability faster than being woken by your own code. This only works if it comes with the authority to fix things - ownership without the ability to change the pipeline, the infrastructure, or the roadmap is just blame. Where full on-call is not possible, at minimum the team owns its error budget and its incident reviews.

**Sequencing across a large organisation.** Do not roll out to everyone at once. Pick two or three teams with real pain and receptive leads, do the work with them, and make the results loud - lead time cut from three weeks to two days is a more persuasive artifact than any strategy document. Then let adoption pull rather than push: teams ask for the paved road because their peers are shipping faster. Reserve mandates for the small set of things that genuinely must be uniform (secret handling, audit trails, supply-chain provenance) and automate those as guardrails in the pipeline rather than as policies people are asked to remember.

**What leadership has to supply.** Slack in the schedule for improvement work (a standing capacity allocation, not "when we have time"), a funded platform team treated as a product team, and consistency - the fastest way to kill the whole effort is to demand daily deployments and then punish the first failed one. If leadership will not fund the slack, say so plainly; culture change without capacity is a request for unpaid overtime.

## Example

```text
Adoption, not mandate

  pain → pilot (2-3 teams) → visible outcome → paved road → pull
   │                                                          │
   └── enabling team embeds, leaves capability ───────────────┘

  Uniform by guardrail (automated, non-negotiable):
     secrets handling · provenance/signing · audit trail · IAM boundaries
  Everything else: opt-in, and cheaper on the road than off it.
```

```yaml
# A paved road is a real artifact, not a wiki page: one template, everything wired.
# backstage/template.yaml (abridged)
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: go-service
  title: Go service (paved road)
spec:
  steps:
    - id: scaffold # repo with CI, tests, Dockerfile, OTel, health endpoints
      action: fetch:template
    - id: pipeline # build, scan, sign, canary deploy - no team wiring required
      action: github:actions:enable
    - id: observability # dashboard, SLO, alert routes created from the start
      action: grafana:dashboard:create
    - id: ownership # CODEOWNERS + on-call rota + catalog entry, non-optional
      action: catalog:register
```

```promql
# Per-team outcome metrics: throughput always paired with stability.
sum by (team) (increase(deployments_total{env="prod"}[7d]))          # frequency
histogram_quantile(0.5, sum by (team, le) (rate(lead_time_seconds_bucket[30d])))
sum by (team) (increase(deployments_failed_total[30d]))
  / sum by (team) (increase(deployments_total[30d]))                 # change failure rate
sum by (team) (increase(pages_total[7d]))                            # operational load
```

## Interview tips

- Open with "you cannot mandate culture, so you change what is easy and what is measured". It reframes the question the way senior interviewers want.
- Name the anti-patterns first - a central DevOps silo, a maturity-model spreadsheet, top-down mandates. Being able to say why the obvious approach fails is the differentiator.
- Be precise about the metric rules: no cross-team league tables, never in performance reviews, always pair throughput with stability.
- Use the enabling-team / community-of-practice language (Team Topologies) but describe the mechanism, not just the label.
- "You build it, you run it" must come with authority to change things. Say that explicitly - it is the difference between ownership and blame.
- Distinguish the small set of things that should be uniform guardrails from everything that should be opt-in. And be ready to say what you need from leadership: funded slack for improvement work.

---

[⬅ Back to DevOps Culture and Practices](./README.md) · [All topics](../README.md)
