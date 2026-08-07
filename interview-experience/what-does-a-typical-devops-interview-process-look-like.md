---
title: "What does a typical DevOps interview process look like?"
id: 272
category: "Interview Experience"
difficulty: "Beginner"
tags:
  - devops
  - interview-experience
  - interview-questions
---

# What does a typical DevOps interview process look like?

**Short answer:** Three to five rounds. A recruiter screen, one or two technical rounds mixing rapid-fire fundamentals with scenario questions, often a hands-on or take-home exercise, then a managerial round about ownership and incidents, and finally HR for compensation and fit. Service companies and consultancies front-load breadth across many tools; product companies go deeper on fewer things and add system design.

## Detail

**The shape, round by round:**

| Round                        | Typically covers                                                                                   | What they are testing                      |
| ---------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| Recruiter screen (20-30 min) | Stack, notice period, compensation, location                                                       | Filtering, not evaluation                  |
| Technical 1 (45-60 min)      | "Explain your project", then fundamentals across Linux, Git, Docker, K8s, CI/CD, Terraform, cloud  | Breadth - do you actually use these daily? |
| Technical 2 (60 min)         | Scenario and troubleshooting: "the Pod is CrashLooping", "state file is gone", "deploy broke prod" | Depth and judgement under ambiguity        |
| Hands-on / take-home         | Write a Dockerfile, a pipeline, a Terraform module, or a script                                    | Whether you can actually build it          |
| Managerial (45 min)          | Ownership, incidents, disagreement, mentoring, on-call                                             | Seniority and collaboration                |
| HR (20-30 min)               | Compensation, notice, motivation                                                                   | Closing                                    |

**Technical round one is a breadth sweep.** In real write-ups this round is almost always the same shape: your project first, then twenty to forty short questions moving quickly across topics. Interviewers are checking that your daily-driver knowledge is real. Answers should be two to four sentences - long monologues on question three mean you never reach the topics you are strongest in.

**Technical round two is where offers are decided.** It is scenario-driven: something is broken, or a design decision needs justifying. There is rarely one right answer; they are watching how you narrow the problem. See [How do you answer scenario-based troubleshooting questions?](./how-do-you-answer-scenario-based-troubleshooting-questions.md).

**Service companies vs product companies.** Consultancies and IT services (the Accenture/Infosys/Capgemini/Deloitte shape) test _breadth_ - you will be asked about Jenkins, Ansible, Terraform, Docker, Kubernetes, AWS, Linux, shell scripting, and Git in a single hour, because you may be staffed onto any of them. Product companies test _depth_ plus system design: fewer topics, harder follow-ups, and a design round like "design a deployment system for 200 services."

**Level changes the emphasis.** Junior and 2-4 year roles lean on definitions and commands. From roughly 5 years, the weight shifts to scenarios, trade-offs, cost, and incidents - and "why did you choose that?" replaces "what is that?". Principal and SRE-track interviews add SLO design, error budgets, capacity planning, and blast-radius reasoning.

**The hands-on round is more common than people expect.** Typical tasks: write a multi-stage Dockerfile for a given app, write a Jenkinsfile or GitHub Actions workflow with build/test/scan/deploy stages, write a Terraform module for an EC2 instance in a VPC, write a shell script to rotate logs or back up a directory, or debug a deliberately broken Kubernetes manifest. Practise typing these without autocomplete.

**Timing and logistics.** Most processes run one to three weeks. Rounds are usually 45-60 minutes on video. Screen-sharing a terminal is common in the hands-on round - have a clean environment ready. Interviewers frequently ask you to draw architecture; a shared whiteboard or even paper on camera works, and using one consistently reads well.

**Preparing efficiently.** Do not try to read everything. Work backwards from the job description: the tools it names are the tools you will be asked about. Then cover the universal core that appears regardless of stack - Linux troubleshooting and text processing, Git, Docker layers and image size, Kubernetes workloads and debugging, Terraform state, one CI/CD tool deeply, and one cloud's IAM and networking model.

## Example

```text
TYPICAL 5-ROUND PROCESS  (mid/senior DevOps, ~2 weeks)

  Day 1   Recruiter screen ......... 25 min   stack, notice, comp range
  Day 4   Technical 1 .............. 60 min   project walkthrough + breadth sweep
  Day 7   Technical 2 .............. 60 min   scenarios, debugging, design trade-offs
  Day 8   Take-home ............... 2-4 hrs   Dockerfile + pipeline + Terraform module
  Day 11  Managerial ............... 45 min   ownership, incidents, conflict, mentoring
  Day 13  HR ....................... 25 min   compensation, start date


WHAT GETS TESTED, BY ROLE SHAPE

  Service company / consultancy      Product company / SRE
  ────────────────────────────       ──────────────────────────
  Breadth across 8-10 tools          Depth on 3-4, plus system design
  "What is X?" / "How do you do X?"  "Why X over Y?" / "What breaks at scale?"
  Tool-by-tool sweep                 Incident + SLO + capacity reasoning
  Client-facing communication        Blast radius and failure modes


UNIVERSAL CORE — asked regardless of the job description

  Linux         troubleshooting, grep/awk/sed, systemd, disk & CPU
  Git           merge vs rebase, undoing changes, branching strategy
  Docker        layers, cache, image size, multi-stage
  Kubernetes    workloads, probes, scheduling, debugging a broken Pod
  Terraform     state, locking, modules, drift
  CI/CD         one tool deeply, end to end, including secrets and scanning
  Cloud         IAM model + networking for your primary provider
  Scripting     Bash first, Python if you claim it
```

## Interview tips

- Ask the recruiter for the round structure and what each one covers. They almost always tell you, and it lets you prepare precisely instead of broadly.
- Keep round-one answers to two to four sentences. Pace matters - they have a list, and you want to reach the topics where you are strong.
- Say "I have not used that, but here is the closest thing I have done" rather than bluffing. Interviewers probe uncertainty, and a confident wrong answer costs more than an honest gap.
- Match your preparation to the company shape: breadth for consultancies, depth plus design for product companies.
- Practise the hands-on tasks by actually typing them. Knowing what a multi-stage Dockerfile looks like is different from writing one under observation.
- Ask what the on-call rotation and incident process look like. It is a genuine question and it signals operational seniority.
- Treat the managerial round as technical too - "tell me about an incident you led" is assessed on the technical detail as much as the narrative.

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
