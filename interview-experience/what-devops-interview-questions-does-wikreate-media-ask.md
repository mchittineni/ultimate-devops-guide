---
title: "What DevOps interview questions does Wikreate Media ask?"
id: 391
category: "Interview Experience"
difficulty: "Beginner"
tags:
  - devops
  - interview-experience
  - interview-questions
  - wikreate-media
  - aws-engineering
  - version-control
  - cicd
  - scalability-and-high-availability
---

# What DevOps interview questions does Wikreate Media ask?

## Questions

**AWS**

- **What is Route 53 used for?**
- **What is the difference between S3 and EBS?**

**Git**

- **What is `git stash`?**
- **What is the difference between `git fetch` and `git pull`?**

**Scaling and delivery**

- **What is the difference between vertical and horizontal scaling?**
- **What is the role of continuous integration?**

## Example

```text
Wikreate Media — DevOps Engineer, reported round
6 questions

  AWS                         2   Route 53, S3 vs EBS
  Git                         2   stash, fetch vs pull
  Scaling and delivery        2   vertical vs horizontal scaling,
                                  role of continuous integration

THE SHORTEST FULL ROUND IN THIS COLLECTION
  Six standard questions with no scenarios — this is an early screening call.
  Every question has a well-known answer, so the differentiator is not
  knowledge but precision: give the definition, then one consequence that
  shows you have actually used it.
```

## Interview tips

- Route 53 should be answered as more than "AWS DNS". It is a managed authoritative DNS service plus health checking and traffic routing, and the parts worth naming are the routing policies — simple, weighted for canaries and A/B splits, latency-based to send users to the nearest region, failover driven by health checks for disaster recovery, and geolocation. Add the two AWS-specific details that show real use: **alias records**, which point at an ALB, CloudFront distribution, or S3 website, work at the zone apex where a CNAME cannot, and are not charged per query; and private hosted zones, which resolve only from inside associated VPCs. Mention that it also acts as a domain registrar. See [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).
- S3 versus EBS is object versus block storage, and the consequences matter more than the labels. S3 is object storage reached over HTTP with effectively unlimited capacity, regional durability, versioning, lifecycle rules, and many concurrent clients — but you cannot mount it as a filesystem and run a database on it. EBS is a block device attached to a single instance in a single availability zone, formatted with a filesystem, with provisioned IOPS and snapshots. Say the deciding question: does the workload need a filesystem and low-latency random writes (EBS) or durable, shareable objects (S3)? Then add the practical constraint people forget — EBS is zonal, so a volume cannot follow an instance to another availability zone, which is why you restore from a snapshot instead. See [S3 storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md).
- `git stash` should come with when you would use it and its limits: it shelves uncommitted changes — tracked modifications and staged content — so you get a clean working tree to switch branches or pull, and `git stash pop` reapplies and drops the entry while `git stash apply` keeps it. Add the details that prove use: `git stash list` to see the stack, `git stash -u` to include untracked files (they are excluded by default, which is the classic surprise), and `git stash push -m "message"` to label one. Then the honest caveat — a stash is easy to forget and easy to lose in a conflict, so a throwaway work-in-progress commit on a branch is often the safer habit. See [undoing changes in Git safely](../version-control/how-do-you-undo-changes-in-git-safely.md).
- `git fetch` versus `git pull` has a crisp answer plus one recommendation: `fetch` downloads new objects and updates your remote-tracking branches, changing nothing in your working tree or current branch; `pull` is `fetch` followed by `merge` (or `rebase` with `--rebase`), so it actually moves your branch. Say that you `fetch` when you want to inspect what changed before integrating, and that `pull --rebase` avoids the merge commits that make history unreadable. See [git merge, rebase, and cherry-pick](../version-control/what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md).
- Vertical versus horizontal scaling is a definitions question with real depth available, so use it. Vertical means a bigger machine — simple, needs no application changes, but has a hard ceiling, usually requires a restart or failover, and leaves you with a single point of failure. Horizontal means more machines behind a load balancer — effectively unbounded and inherently more resilient, but it requires the application to be **stateless**, with session state externalised to Redis or a database, and it moves the bottleneck to whatever is not horizontally scalable, which is almost always the write path of the database. Say that sentence about the database, because it is the insight the question is really probing: you scale the stateless tier out and the data tier up, until you need read replicas, caching, or sharding. See [scalability in DevOps](../scalability-and-high-availability/what-is-scalability-in-devops.md) and [auto-scaling](../scalability-and-high-availability/what-is-auto-scaling.md).
- "The role of continuous integration" invites a textbook answer, so give the _purpose_ rather than the mechanics: CI exists to keep the main branch continuously in a known-good, releasable state by having every developer integrate small changes frequently and having an automated build plus test suite verify each one — so integration problems surface in minutes rather than at the end of a release cycle. Then name what makes it real: it must be fast enough that people wait for it, it must be trusted (a flaky suite trains people to ignore red builds), and it must actually block the merge through branch protection. Say that CI is about _feedback speed_, and that CD is a separate question about what happens after the build is green. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md) and [continuous delivery versus continuous deployment](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md).
- In a six-question round every answer carries roughly 17%, so the pattern that wins is: definition in one sentence, mechanism in one more, then one trade-off or consequence, then stop. Do not pad — but do volunteer the adjacent detail (alias records, `stash -u`, why horizontal scaling needs statelessness), because with so few questions that is the only way to show depth. See [what are the most frequently asked DevOps interview questions](./what-are-the-most-frequently-asked-devops-interview-questions.md) for the wider recall checklist these six are drawn from.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#20`): [What is the difference between Continuous Delivery and Continuous Deployment?](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
