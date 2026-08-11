---
title: "What DevOps interview questions does Accolite ask?"
id: 309
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - accolite
  - scripting-and-automation
  - database-management-in-devops
  - cicd
  - kubernetes
---

# What DevOps interview questions does Accolite ask?

## Questions

**Python**

- **Write a Python script that watches a directory and, once a minute, prints the names of any files that have appeared since the last check.**
- **What is the difference between a `set` and a `list` in Python, and why does that matter for the directory-watching script you just wrote?**
- **Write a Python function that takes a list of dictionaries representing job logs and returns the job IDs whose `status` is `FAILED`.**
- **Given the sample log list, trace your function by hand and state the exact output.** The sample in the original write-up is garbled by copy-paste, but its shape is four records with `job_id`, `status`, and `timestamp` keys, of which jobs 102 and 103 are `FAILED`.

**SQL**

- **Given `Customers(customer_id, customer_name)` and `Orders(order_id, customer_id, order_date, amount)`, write a query returning the names of customers who placed more than three orders in the last 90 days.**

**Platform concepts**

- **What is CI/CD? Explain it briefly and concretely.**
- **Explain the Kubernetes architecture, naming each component and what it is responsible for.**
  **How the round was run** — the candidate's own closing note, worth more than any single question:

- **Expect a follow-up on every answer: explain it briefly, explain the code, explain how it is used, and state the output.**

## Example

```text
Accolite — DevOps Engineer (3 YOE), reported round
7 questions

  Python                      4   directory watcher, set vs list,
                                  filter FAILED jobs, trace the output
  SQL                         1   >3 orders in 90 days (GROUP BY + HAVING)
  Platform concepts           2   CI/CD, Kubernetes architecture

UNUSUAL FOR A DEVOPS ROUND
  5 of 7 questions require writing code, and every answer was followed by
  "what will the output be?" This is a coding screen wearing a DevOps label.
```

```sql
-- The expected shape of the SQL answer: aggregate, then filter the aggregate.
SELECT c.customer_name
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY c.customer_id, c.customer_name
HAVING COUNT(*) > 3;
```

## Interview tips

- The `set` versus `list` question is not trivia — it is checking whether you realised the directory watcher needs a set. Keep the previous listing in a `set` and use set difference to find new files; membership testing is O(1) rather than O(n). Say that connection out loud.
- For the directory watcher, mention the trade-off between polling on a timer and watching kernel events (`inotify`, or the `watchdog` library). Polling is simpler and portable; `inotify` is immediate and cheaper. Naming both is what separates a scripted answer from a considered one. See [what you use Python for as a DevOps engineer](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md).
- On the SQL question, the trap is filtering with `WHERE COUNT(*) > 3`. Aggregates are filtered in `HAVING`, and the date window belongs in `WHERE` so it narrows rows before grouping.
- Because every answer is followed by "what is the output", dry-run your code aloud with the sample input before declaring it finished. Catching your own off-by-one is a strong signal.
- Guard the FAILED-jobs function against real-world log data: use `record.get("status")` rather than `record["status"]`, and consider case-insensitive comparison. The garbled sample in the original write-up even contains a misspelled `job_jd` key, which is exactly the kind of defect the interviewer may be probing for.
- The two concept questions are short, so answer them tightly and completely. For Kubernetes, walk the control plane (API server, etcd, scheduler, controller manager) then the node (kubelet, kube-proxy, runtime), and finish with the reconciliation loop. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md) and [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md).
- Bash would be a defensible answer for the directory watcher, but they explicitly asked for Python. Follow the constraint given. See [when to use Bash and when to use Python](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
