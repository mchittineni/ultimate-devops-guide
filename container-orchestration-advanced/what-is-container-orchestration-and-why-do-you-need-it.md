---
title: "What is container orchestration and why do you need it?"
id: 284
category: "Container Orchestration Advanced"
difficulty: "Beginner"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
---

# What is container orchestration and why do you need it?

**Short answer:** Container orchestration is the automation of placing, running, connecting, scaling, and replacing containers across a pool of machines. You need it as soon as you have more containers than you can hold in your head - because the work it does (deciding which machine has room, restarting what died, load balancing across replicas, rolling out a new version without downtime) is work you would otherwise do by hand, at 3am.

## Detail

**The problem it solves.** Docker runs a container on _one_ machine. That leaves you answering, manually, every one of these questions:

- Which of my ten servers has enough CPU and memory for this container?
- This container just crashed - who restarts it?
- I need five copies of the API. How does traffic find the healthy ones?
- I am deploying v2. How do I replace v1 gradually and stop if it fails?
- The container needs a database password. Where does it come from safely?
- Server 3 died. Who moves its containers somewhere else?

An orchestrator answers all of them from a declarative description of the desired state. You say "five replicas of this image, reachable on port 80, with these resource requests"; the orchestrator continuously compares that to reality and closes the gap.

**The core capabilities, in the order you notice needing them:**

| Capability             | What it means in practice                                            |
| ---------------------- | -------------------------------------------------------------------- |
| **Scheduling**         | Picks a node with capacity that satisfies your constraints           |
| **Self-healing**       | Restarts failed containers, replaces containers on dead nodes        |
| **Service discovery**  | A stable name and virtual IP in front of a changing set of replicas  |
| **Load balancing**     | Spreads traffic across healthy replicas only                         |
| **Scaling**            | Adds or removes replicas from a metric, and nodes to fit them        |
| **Rolling updates**    | Replaces old versions incrementally, and rolls back on failure       |
| **Config and secrets** | Injects configuration at runtime instead of baking it into the image |
| **Storage**            | Attaches persistent volumes to the container that needs them         |

**The declarative loop is the key idea.** You do not issue commands ("start a container here"); you submit desired state and controllers reconcile toward it forever. That is why a killed Pod comes back, and why `kubectl delete pod` is not how you scale down. Understanding this single mechanism explains most orchestrator behaviour that surprises newcomers.

**The options.** **Kubernetes** is the de facto standard and where the ecosystem lives - usually consumed as a managed service (EKS, AKS, GKE). **Docker Swarm** is far simpler and still fine for small estates, but has little momentum. **Nomad** is a lighter scheduler that also handles non-container workloads. **ECS** (with Fargate) and **Cloud Run / Container Apps** are managed platforms that give you most orchestration benefits without a cluster to operate - frequently the right choice for a small team.

**When you do _not_ need it.** Three containers on one host with Docker Compose, or a single service on a PaaS, is a legitimate architecture. Kubernetes brings real operational cost: upgrades, RBAC, networking, resource tuning, and a large surface to secure. Adopt it when the scale, the number of teams, or a specific requirement justifies it - not because it is on the job description.

## Example

```yaml
# Desired state, declared. The orchestrator's job is to keep reality matching this.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3 # self-healing target: always three healthy Pods
  selector:
    matchLabels: { app: api }
  strategy:
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 } # no-downtime updates
  template:
    metadata:
      labels: { app: api }
    spec:
      containers:
        - name: api
          image: myapp:1.4.0
          ports: [{ containerPort: 8080 }]
          resources: # what the scheduler uses to pick a node
            requests: { cpu: 100m, memory: 128Mi }
            limits: { memory: 256Mi }
          readinessProbe: # only receive traffic when actually ready
            httpGet: { path: /healthz, port: 8080 }
          env:
            - name: DB_PASSWORD # config injected, not baked into the image
              valueFrom:
                secretKeyRef: { name: db, key: password }
---
apiVersion: v1
kind: Service # stable name + load balancing over whichever Pods are healthy
metadata:
  name: api
spec:
  selector: { app: api }
  ports: [{ port: 80, targetPort: 8080 }]
```

```bash
kubectl get deploy api          # desired vs current vs ready - the reconciliation gap
kubectl delete pod api-xxxx     # watch it come back: you cannot scale down this way
kubectl scale deploy api --replicas=5
kubectl set image deploy/api api=myapp:1.5.0   # rolling update
kubectl rollout undo deploy/api                # and the rollback
```

## Interview tips

- Frame it as "the work you would otherwise do manually" and list scheduling, self-healing, discovery, scaling, and rolling updates. Concrete beats abstract.
- Explain the declarative reconciliation loop in one sentence. It is the concept that separates people who have read about Kubernetes from people who have used it.
- Be able to say what Docker alone does _not_ do: one host, no scheduling across machines, no self-healing across node failure.
- Name the alternatives and give ECS/Fargate or Cloud Run as legitimate answers for small teams. Recommending Kubernetes unconditionally is a red flag.
- Mention that resource `requests` are what the scheduler reads. It is a small detail that lands well.
- If asked "when would you not use Kubernetes?", say three containers on one host, a single-team app, or no capacity to operate a cluster. Honesty scores here.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
