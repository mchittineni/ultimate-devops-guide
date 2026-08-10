---
title: "What cloud engineering interview questions does Turning ask?"
id: 386
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - turning
  - aws-engineering
  - infrastructure-as-code
  - serverless-architecture
  - version-control
  - database-management-in-devops
  - devops-tools-and-automation
---

# What cloud engineering interview questions does Turning ask?

## Questions

**Databases and failover**

- **A database failover happens and the connection switches from A to B. If a user is writing data during that interval, how do you manage it?**

**Serverless**

- **What is a Lambda cold start?**
- **You have a payment gateway application running in Lambda and sometimes it fails to reach an external API. How do you diagnose and fix that while a payment is being processed?**
- **Write a script that checks whether the external API is reachable before starting the request.**

**Infrastructure as code**

- **What are the AWS CDK commands?**
- **How do you implement Terraform in a CD pipeline?**
- **Someone manually changed the configuration of an EC2 instance that was created through Terraform. How do you fix it?**

**Git**

- **Ten developers are checking in code to Git. How do you remove the check-in made by developer ten?**

**Deployment**

- **What is the purpose of blue-green deployment, and how do you switch back between deployments?**

## Example

```text
Turning — Cloud Engineer, reported round
9 questions

  Serverless                  3   Lambda cold start, payment gateway failing
                                  to reach an external API, reachability script
  Infrastructure as code      3   CDK commands, Terraform in a CD pipeline,
                                  manual change to a TF-managed instance
  Databases and failover      1   in-flight writes during a failover
  Git                         1   remove one developer's commit out of ten
  Deployment                  1   blue-green purpose and switching back

THE QUESTION THAT DECIDES THE ROUND
  "A user is writing data while the database fails over." It is the only
  question here about correctness rather than tooling, and the honest answer
  involves admitting that some writes are simply lost.
```

## Interview tips

- The failover-during-a-write question is the best one here, and the answer must start with the uncomfortable truth: an in-flight transaction that has not been committed and acknowledged is **lost**. The connection to A is severed, the client gets an error, and with asynchronous replication anything committed on A but not yet replicated is gone too — which is exactly what RPO measures. Then give what you actually do about it. On the client side: connection pools must detect the broken connection and reconnect rather than holding a stale one, the driver should use the cluster or failover endpoint rather than an instance address so DNS re-resolution finds B, and DNS caching in the JVM or the OS must be short or failover appears to hang. On the application side: retry with exponential backoff, and make writes **idempotent** with a client-generated request or transaction ID so a retry after an ambiguous failure does not double-charge anyone. On the platform side: Multi-AZ with synchronous replication reduces the loss window to near zero, an RDS Proxy holds connections and shortens failover, and a transactional outbox or a queue in front of the write path means the request survives the database being briefly unavailable. Say "idempotency keys plus retries, and synchronous replication to shrink the RPO" — for a payments-adjacent role that is the answer they want. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- The payment-gateway question follows directly, and the trap is answering "add a retry". Diagnose first: check whether the failures correlate with cold starts, whether the function is in a VPC and therefore depends on a NAT gateway that may be saturated or missing a route, whether the external API is rate-limiting or its TLS certificate rotated, whether DNS resolution is failing intermittently, and whether the function timeout is shorter than the API's slow-path latency so you are aborting rather than being refused. Then the fix, and be careful about it: for a _payment_, blind retries are dangerous, so the correct pattern is an idempotency key sent with the request so the provider deduplicates, a circuit breaker so you fail fast rather than piling up, a queue (SQS with a dead-letter queue) so a failed attempt is durable and retried out-of-band rather than lost, and reconciliation against the provider afterwards to resolve any ambiguous outcome. Say explicitly that "did the charge happen?" is the question that matters, and that only idempotency plus reconciliation answers it. Add X-Ray tracing and structured logging with the correlation ID so you can prove what happened for a specific transaction.
- The reachability-script question has a subtlety worth raising: a pre-flight check does not remove the race, because the API can become unreachable between your check and your real request. So write the script — a `curl` with `--max-time` and `-o /dev/null -w '%{http_code}'`, or a small Python `requests` call with a timeout, exiting non-zero on failure — and then say that in production you would rely on a timeout plus retry plus circuit breaker on the actual call rather than a separate probe, because the probe is only ever a hint. Naming that limitation is what distinguishes the answer. See [writing a production-grade Bash script](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md).
- The Git question is deliberately ambiguous and clarifying it is the correct move: "remove developer ten's check-in" means something different depending on whether it is already on the shared branch. If it is the most recent commit and not yet pushed anywhere others depend on, `git reset --hard HEAD~1` locally. If it is already on the shared branch, **`git revert <sha>`** is the right answer — it creates a new commit undoing the change and preserves history, which is safe for everyone else. If it is one commit buried in a series and you must genuinely erase it, `git rebase -i` dropping that commit, or `git filter-repo` for something that must be removed entirely such as a leaked secret — followed by `git push --force-with-lease` and telling the other nine developers to re-clone or reset, because you have rewritten shared history. Say the rule: revert on shared branches, rewrite only when you must and never silently. See [undoing changes in Git safely](../version-control/how-do-you-undo-changes-in-git-safely.md) and [recovering from a bad Git history rewrite](../version-control/how-do-you-recover-from-a-bad-git-history-rewrite.md).
- The manually-changed-EC2 question is a drift question, and the answer depends on intent — say both branches. If the manual change was wrong, `terraform plan` shows the drift and `terraform apply` reverts the resource to the declared state. If the manual change was _correct_ and should be kept, update the configuration to match it and confirm the plan is then empty, or add `lifecycle { ignore_changes = [...] }` for the specific attribute you do not want to manage. Then the prevention, which is what they are really testing: deny console write access to the pipeline's resources via IAM or an SCP, apply only from CI, and run `terraform plan -refresh-only` on a schedule so drift is detected before it surprises you. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- Terraform in a CD pipeline should be described as a gated two-phase flow: on the pull request, `init` with a remote backend, `fmt -check`, `validate`, a security scan with Checkov or tfsec, then `plan -out=tfplan` with the plan posted as a comment for review; on merge, `apply tfplan` — applying the **saved plan file** so what runs is provably what was reviewed. Add the surrounding controls: state locking so concurrent applies cannot race, OIDC federation to AWS so there is no stored access key, an approval gate before production, and separate state per environment. Saying "apply the saved plan, not a fresh one" is the detail that matters most. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md).
- For CDK, give the command lifecycle rather than a random list: `cdk init` to scaffold, `cdk bootstrap` to create the deployment resources in the account and region — the step people forget, and the usual cause of a first-deploy failure — `cdk synth` to render CloudFormation, `cdk diff` to compare against what is deployed, `cdk deploy`, and `cdk destroy`. Then the conceptual point: CDK is a synthesiser that produces CloudFormation, so the actual deployment is a CloudFormation stack — which is why `cdk diff` is the CDK equivalent of `terraform plan`. See [when to choose CloudFormation, CDK, or Terraform on AWS](../aws-engineering/when-do-you-choose-cloudformation-cdk-or-terraform-on-aws.md).
- Lambda cold start needs the mechanism then the mitigations: the cold start is the time to provision an execution environment, download and initialise the runtime and your package, and run any code outside the handler — so it affects the first invocation and every scale-out, not steady state. Mitigations in order of effectiveness: provisioned concurrency for predictable latency, SnapStart for Java, a smaller deployment package with fewer dependencies, moving SDK client construction and connection setup outside the handler so it is reused across invocations, and avoiding VPC attachment unless private resources genuinely require it. Tie it back to the payment-gateway question — an intermittent external-API failure that only happens on the first request after idle is very often a cold-start timeout.
- Blue-green should be answered with purpose, mechanism, and the switch-back path, since they asked for all three. Purpose: eliminate deployment risk by bringing a complete second environment up, validating it, then cutting traffic over in one atomic step — so rollback is instant rather than another deployment. Mechanism for switching: in Kubernetes, patch the Service's label selector from `version: blue` to `version: green`; on AWS, change the ALB listener rule's target group or shift the weighted forward action. Switching _back_ is the same operation in reverse, which is only possible because you kept the old version running — so say that you keep blue warm for a defined soak window before tearing it down, and that the constraint that usually rules blue-green out is a shared database schema that must satisfy both versions at once. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
