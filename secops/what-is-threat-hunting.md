---
title: "What is threat hunting?"
id: 173
category: "SecOps and Threat Detection"
difficulty: "Advanced"
tags:
  - devops
  - secops
  - interview-questions
---

# What is threat hunting?

**Short answer:** Threat hunting is the proactive search for adversary activity that existing detections did not catch. It is hypothesis-driven — you state what an attacker would look like in your telemetry, query for it, and either find something or convert the hunt into a new detection. Its main output is usually not an incident but improved coverage.

## Detail

**Hypothesis first.** "Let us look at the logs" is browsing, not hunting. A usable hypothesis is specific and falsifiable: _"If an attacker had stolen a CI service account token, we would see that identity calling the Kubernetes API from outside our runner IP ranges."_ That sentence names the data source, the query, and what a positive result looks like.

**Where hypotheses come from:** threat intelligence about groups targeting your sector, a technique from the ATT&CK matrix you cannot yet detect, the assumption of a known weakness in your own architecture ("what would abuse of this over-privileged role look like?"), and anomalies noticed during unrelated work.

**Three common styles.** _Intel-driven_ — start from a reported campaign's behaviour. _Hypothesis-driven_ — as above, from your own threat model. _Baseline/anomaly-driven_ — build the normal profile of something (which service accounts touch this namespace, which countries authenticate) and investigate the outliers. Baselining is the most productive in cloud environments, where "normal" is narrow and machine-generated.

**Every hunt has one of three outcomes**, and all are valuable: an incident is opened; a new detection rule is written; or a telemetry gap is identified and becomes platform work. A hunt that finds nothing and produces nothing was scoped badly.

**Document and repeat.** Hunts live as notebooks or saved queries with their hypothesis, data sources, query, and findings, so they can be re-run after the environment changes. Recurring hunts that stay valuable should graduate into scheduled detections — hunting is where detections come from.

**Prerequisites people underestimate:** enough retained telemetry (90 days minimum for scoping), an asset and identity inventory to define "normal", and analyst time that is protected from the alert queue. Without protected time, hunting is always deferred.

## Example

```sql
-- Hunt: service-account tokens used from outside the CI egress ranges
-- Hypothesis: a stolen CI token would authenticate from an unexpected network
SELECT user.username, sourceIPs[1] AS src_ip, verb, objectRef.resource, count(*) AS calls
FROM k8s_audit
WHERE timestamp > now() - INTERVAL 30 DAY
  AND user.username LIKE 'system:serviceaccount:ci:%'
  AND NOT is_in_cidr(sourceIPs[1], ['10.20.0.0/16', '52.31.44.0/24'])
GROUP BY 1, 2, 3, 4
ORDER BY calls DESC;
```

## Interview tips

- State a concrete hypothesis out loud — that single sentence is what interviewers are listening for.
- "A hunt that finds nothing still produces a detection or a telemetry gap" is a strong, mature framing.
- Expect: "how is this different from monitoring?" — monitoring answers known questions automatically; hunting asks new ones and then automates them.

---

[⬅ Back to SecOps and Threat Detection](./README.md) · [All topics](../README.md)
