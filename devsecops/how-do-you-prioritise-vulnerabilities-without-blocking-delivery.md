---
title: "How do you prioritise vulnerabilities without blocking delivery?"
id: 168
category: "DevSecOps"
difficulty: "Advanced"
tags:
  - devops
  - devsecops
  - interview-questions
---

# How do you prioritise vulnerabilities without blocking delivery?

**Short answer:** Rank by exploitability and exposure rather than CVSS score alone: is it in CISA's Known Exploited Vulnerabilities catalogue, what is its EPSS probability, is the vulnerable code reachable, is the workload internet-facing, and does a fix exist? Then set remediation SLAs per band, gate only on newly introduced findings, and burn the backlog down on its own track.

## Detail

**Why CVSS alone fails.** CVSS is severity in the abstract, assigned once, ignoring your deployment. CVSS v4.0 improved this - it splits Base from Threat, Environmental, and Supplemental metrics precisely so you can re-score for your context - but almost nobody consumes anything beyond the Base score that the feed hands them, so the practical failure mode is unchanged. A CVSS 9.8 in a library you never call, on an internal batch job, is not the emergency that a CVSS 7.5 in your public API's request parser is. Most organisations that gate on "no highs" end up with thousands of exceptions and no signal.

**The signals worth combining:**

| Signal           | Question it answers                          | Source                        |
| ---------------- | -------------------------------------------- | ----------------------------- |
| KEV              | Is it being exploited in the wild right now? | CISA KEV catalogue            |
| EPSS             | Probability of exploitation in 30 days       | FIRST EPSS scores             |
| Reachability     | Does our code call the vulnerable function?  | SCA with call-graph analysis  |
| Exposure         | Internet-facing? Handles untrusted input?    | your own asset inventory      |
| Fix availability | Is there a patched version?                  | advisory / `--ignore-unfixed` |

**Publish SLAs and measure them.** For example: KEV or actively exploited - 48 hours; critical and reachable and exposed - 7 days; high - 30 days; everything else - next dependency-bump cycle. What matters is that the numbers are agreed with engineering leadership and that you report attainment, not that they are aggressive.

**Automate the boring 80%.** Most findings are fixed by a patch-version bump. Renovate or Dependabot with automerge for patch updates and a green test suite removes the majority of the queue without a human decision. Reserve triage effort for major-version bumps and unfixable findings.

**When there is no fix.** Compensating controls (WAF rule, network policy, feature disabled, input validated), a recorded risk acceptance with an owner and an expiry date, and a monitored ticket. "Wait for upstream" is a decision only if someone is watching for the release.

**Base images dominate the count.** Rebuilding weekly on a patched, minimal base (distroless, Alpine, Chainguard-style) often removes more findings than any application change. Track "findings inherited from base image" separately so application teams are not blamed for them.

## Example

```bash
# Only findings that are fixable and reachable break the build; the rest go to the backlog queue
trivy image --severity HIGH,CRITICAL --ignore-unfixed \
  --exit-code 1 ghcr.io/acme/api@"$DIGEST"

# Enrich the full report with EPSS/KEV for backlog ranking
trivy image --format json ghcr.io/acme/api@"$DIGEST" > findings.json
python3 rank.py findings.json --kev kev.json --epss epss.csv --top 20
```

## Interview tips

- Naming KEV and EPSS immediately signals current practice; CVSS-only answers read as dated.
- "Gate on new findings, SLA the backlog" is the sentence that shows you have kept a pipeline usable.
- Expect: "a critical with no patch, shipping tomorrow - what do you do?" Answer with compensating control, time-boxed risk acceptance, and who signs it.

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
