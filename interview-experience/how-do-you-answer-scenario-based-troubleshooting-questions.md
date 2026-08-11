---
title: "How do you answer scenario-based troubleshooting questions?"
id: 273
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
---

# How do you answer scenario-based troubleshooting questions?

**Short answer:** Do not jump to a cause. Clarify the symptom and blast radius, state what you would check first and why, then narrow layer by layer - naming the exact command at each step - and finish with the fix plus what you would change so it cannot recur. The interviewer is assessing your **method**, not whether you happen to guess the cause they had in mind.

## Detail

**What is actually being tested.** Scenario questions have no single correct answer. A candidate who says "it's DNS" and is right scores worse than one who says "let me check whether it's DNS, TCP, TLS, or the app - here is how I'd tell them apart in one command." They are looking for: do you narrow systematically, do you know real commands, do you consider blast radius, and do you close the loop with prevention.

**A five-step method that works for any scenario:**

1. **Clarify the symptom.** What exactly is failing, for whom, since when, and is it total or partial? "Is it all users or one region? Did it start after a deploy?" Asking this is not stalling - it is the first thing you would do in a real incident, and interviewers score it.
2. **Establish blast radius and stop the bleeding.** Is customer traffic affected right now? If a recent deploy correlates, roll back _first_ and diagnose after. Saying this explicitly signals production experience: mitigation precedes root cause.
3. **Narrow by layer.** Work down the request path - DNS, network, TLS, load balancer, ingress, Service, Pod, application, database - and say which command distinguishes each. Halve the search space with each check rather than checking things at random.
4. **Name the actual command.** `kubectl describe pod`, `kubectl logs --previous`, `dig +trace`, `curl -w`, `df -h`, `terraform plan -detailed-exitcode`. This is the difference between someone who has debugged and someone who has read about debugging.
5. **Close with prevention.** "The fix was X. To stop it recurring I'd add an alert on Y, a policy check in CI, and a runbook entry." Almost nobody does this unprompted, and it is what senior interviews are scoring.

**Think aloud.** Silence reads as being stuck. Narrate the hypothesis you are testing and what result would confirm or eliminate it. It also lets the interviewer redirect you before you spend five minutes down the wrong path - which they usually will, because they want you to succeed.

**Ask for information you would have in reality.** In a real incident you have dashboards, logs, and a deploy timeline. It is entirely legitimate to say "I'd check the deploy timeline first - did anything ship in the last hour?" Interviewers will hand you the answer, and asking scores better than assuming.

**Say "what changed?" early.** The overwhelming majority of production incidents are caused by a change - a deploy, a config edit, a certificate expiry, a dependency upgrade, or a scaling event. Correlating the symptom start time with the change log is the single highest-yield first move, and stating it is a strong signal.

**The scenarios that recur most in real interviews:**

| Scenario                                 | First moves                                                                                                |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Pod stuck `Pending` / `CrashLoopBackOff` | `kubectl describe pod` events; `logs --previous`; resources, image pull, PVC, taints                       |
| Site returns 502 / 504                   | 502 = bad backend response, 504 = timeout; check EndpointSlices, readiness probes, then downstream latency |
| Terraform state deleted                  | **Stop.** Do not apply. Restore a bucket version; import as last resort                                    |
| Disk full on a production host           | `df -h`, then `du -xh --max-depth=1 /`; check deleted-but-open files with `lsof +L1`; rotate logs          |
| High CPU on a node                       | `top`, `pidstat`; is it one process, throttling, or a noisy neighbour Pod without limits?                  |
| Deploy broke production                  | Roll back first; then compare the diff, the config, and the migration                                      |
| Certificate expired                      | Confirm with `openssl s_client`; reissue; then fix the automation and the expiry alert                     |
| Pipeline suddenly slow                   | Which stage? Cache miss, runner contention, or a dependency mirror                                         |
| Secret leaked into Git                   | **Rotate the credential first**; then purge history and add scanning                                       |

**Do not fabricate.** If you have never handled the scenario, say what you would do and reason from first principles. "I have not hit this exact case, but it looks like an ingress-to-Service mismatch, and here is how I would confirm" is a perfectly strong answer.

## Example

```text
SCENARIO: "Users report the site is down. What do you do?"

WEAK ANSWER
  "I'd check the Pods and restart them."
  → no clarification, no method, no blast radius, no prevention

STRONG ANSWER — narrate this shape

  1. CLARIFY
     "Is it total or partial? All regions or one? When did it start?
      Do we have an alert, or is this a user report? Anything deployed
      in the last hour?"

  2. STOP THE BLEEDING
     "If it correlates with a deploy, I roll back before diagnosing.
      Mitigation first, root cause after."

  3. NARROW BY LAYER — one command per layer
     DNS?      dig +short api.acme.com          # resolving, and to the right IP?
     Network?  nc -vz api.acme.com 443          # reachable at all?
     TLS?      openssl s_client -connect ...    # expired or wrong chain?
     Timing?   curl -w 'dns=%{time_namelookup} tls=%{time_appconnect} ttfb=%{time_starttransfer}'
                                                # isolates the failing layer in one call
     Backends? kubectl get endpointslices -l kubernetes.io/service-name=api
                                                # 502/503 usually means zero healthy endpoints
     Pods?     kubectl get pods -l app=api
               kubectl describe pod <name>      # events explain Pending / CrashLoop
               kubectl logs <name> --previous   # why the last container died
     App?      logs, traces, DB connection pool, downstream latency

  4. FIX
     "Say readiness probes were failing because the DB connection pool
      was exhausted - I'd scale the pool or the replicas, confirm
      endpoints return, and verify with synthetic traffic."

  5. PREVENT  ← the step almost everyone skips
     "Then: alert on healthy-endpoint count hitting zero, add a
      burn-rate alert on the availability SLO, cap the pool in config
      review, and write the runbook entry. Blameless postmortem with
      an owner and a date for each action item."
```

## Interview tips

- Never open with a cause. Open with a clarifying question - it is what you would do in a real incident and it is explicitly scored.
- Say "mitigate first, diagnose second" when a deploy is implicated. Rolling back before root-causing is the production instinct they are checking for.
- Ask "what changed?" early. Most incidents are change-induced, and it is the highest-yield first move.
- Name real commands. Vague layers without commands reads as theoretical.
- Always finish with prevention - alert, guardrail, runbook, postmortem action. This is the single easiest way to sound senior, and most candidates omit it.
- Think out loud so the interviewer can redirect you. Silence looks like being stuck even when you are thinking.
- If you do not know, reason from first principles and say so. Confident fabrication is the fastest way to fail the round.
- Related deep-dives worth reading first: [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md), [recovering a lost Terraform state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md), and [what happens when a user opens your application](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
