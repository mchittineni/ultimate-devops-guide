---
title: "What is Cutover Planning and how do maintenance windows, rollback triggers, and DNS TTLs ensure success?"
id: 696
category: "Cloud Migration"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cloud-migration
  - cutover
  - dns
  - rollback
  - incident-management
quiz:
  stem: "Why must engineering teams lower their domain's DNS Time-To-Live (TTL) to 60 seconds several days before a production cloud cutover?"
  options:
    - "DNS servers refuse to update records with TTLs higher than 300 seconds"
    - "To ensure that recursive resolvers clear their caches quickly, allowing global traffic to switch to the new cloud endpoint in seconds and enabling instant rollback if needed"
    - "To reduce DNS query costs"
    - "Because cloud load balancers cannot resolve long TTLs"
  answer: 2
  explanation: "If TTL remains at 24 hours, client DNS resolvers cache the old IP for a day. Lowering TTL to 60s ensures traffic switches to the new cloud IP within one minute and allows instant rollback."
---

# What is Cutover Planning and how do maintenance windows, rollback triggers, and DNS TTLs ensure success?

**Short answer:** Cutover planning is the choreography of the final transition from on-premise to cloud; it requires pre-lowering DNS TTLs to 60s days in advance, establishing a strict Go/No-Go decision matrix, setting definitive rollback triggers, and conducting dry runs.

## Detail

The final cutover is where migrations succeed or fail, because it is the one step that cannot be fully tested in isolation. Good cutover planning makes it boring: rehearsed, timed, with pre-agreed decision points.

### Essential elements of a cutover plan

1. **DNS TTL reduction, done early.**
   - Resolvers cache a record for its TTL, so a record with a TTL of an hour (or a day, which is common for records nobody expected to change) keeps sending clients to the old site that long after you switch.
   - **Best practice**: lower the TTL to about 60 seconds at least one full old-TTL period before cutover (for a 24-hour TTL, more than a day ahead - a week is common), then raise it again after the migration settles.
   - **Caveats**: some clients ignore or extend TTLs (JVMs with long `networkaddress.cache.ttl`, connection pools that never re-resolve, corporate proxies), so plan to restart or recycle those clients, and prefer a traffic layer you control (a load balancer, proxy, or weighted DNS) over relying on TTL alone.
2. **A minute-by-minute runbook** with exact commands, a single owner per step, expected duration, and verification for each:
   - `02:00 UTC - Stop on-prem batch jobs and disable the VM crontab (owner: batch lead)`
   - `02:15 UTC - Confirm replication lag = 0 and validation clean (owner: DBA)`
   - `02:25 UTC - Switch the Route 53 record to the cloud ALB (owner: network lead)`
   - `02:30 UTC - Smoke tests and synthetic transactions pass (owner: QA lead)`
3. **Go/no-go criteria** checked before the window starts: replication lag, test results, rollback readiness, key people present, no conflicting change freeze.
4. **Rollback triggers and a point of no return.** Explicit, measurable conditions that force rollback ("if verification is not green by 04:00 UTC, or error rate exceeds 2% for 10 minutes, roll back"), decided in advance so nobody negotiates at 3 a.m. The point of no return is the step after which rollback means data reconciliation - typically when writes begin on the new system without reverse replication.
5. **Dress rehearsals** of the whole runbook in a production-like environment, timed, until the timings are predictable.
6. **Communication plan**: status page, stakeholder updates at fixed times, and a single incident-style channel for the cutover team.

**Trade-offs.** A shorter window means more automation and rehearsal effort up front; a longer window lowers pressure but increases business impact. Reverse replication extends the rollback window but adds complexity. Weighted or cohort-based cutovers reduce risk but require both environments to run, and serve traffic, at the same time.

## Example

```bash
# T-7d: drop the TTL (the old TTL was 86400, so this must happen more than a day before cutover).
cat > ttl.json <<'JSON'
{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{
  "Name":"app.example.com","Type":"CNAME","TTL":60,
  "ResourceRecords":[{"Value":"onprem-lb.example.com"}]}}]}
JSON
aws route53 change-resource-record-sets --hosted-zone-id "$ZONE" --change-batch file://ttl.json

# T-0: confirm what resolvers actually see before and after the switch.
dig +noall +answer app.example.com @1.1.1.1
dig +noall +answer app.example.com @8.8.8.8
# app.example.com.  60  IN  CNAME  onprem-lb.example.com.   <- TTL already 60: safe to switch

# Rollback trigger check, run every minute during the window.
curl -s "$PROM/api/v1/query" --data-urlencode \
  'query=sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))' \
  | jq -r '.data.result[0].value[1]'    # > 0.02 for 10 minutes -> execute rollback
```

## Interview tips

- Explain why TTLs matter mechanically - resolver caching - and that the TTL must be lowered at least one old-TTL period in advance.
- Mention clients that ignore TTLs (JVM caches, long-lived connection pools) and plan to recycle them.
- Describe the runbook: timed steps, single owners, verification per step.
- Define rollback triggers and the point of no return before the window, not during it.
- Insist on dress rehearsals - the timings they produce are what make the window credible.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
