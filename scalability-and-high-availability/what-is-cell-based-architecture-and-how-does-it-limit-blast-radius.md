---
title: "What is cell-based architecture and how does it limit blast radius?"
id: 774
category: "Scalability and High Availability"
difficulty: "Advanced"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - cell-based-architecture
  - blast-radius
  - resilience
---

# What is cell-based architecture and how does it limit blast radius?

**Short answer:** A cell-based architecture runs many complete, independent copies of a service stack - **cells** - each serving a fixed subset of customers, with a thin **cell router** in front that sends every request to its customer's cell. A failure, bad deployment, poison request, or noisy tenant then affects only the customers in one cell (roughly 1/N of them) instead of everyone. Cells also give you a fixed, tested unit of scale: you grow by adding cells, not by making one deployment ever bigger. The costs are the router, cross-cell operations (migrating customers, global queries), and running N copies of everything.

## Detail

**Why availability zones are not enough.** Multi-AZ protects against infrastructure failure, but most large outages are caused by a change or an unexpected input: a bad config pushed everywhere, a query pattern that melts the shared database, a single tenant's traffic spike. Those failures are not zonal. They hit every replica at once because every replica shares the same deployment, the same data, and the same customers. Cells partition by **customer**, so the same failure is contained.

**The components**

- **Cell.** A full stack - compute, data store, queues, caches - that can serve its customers with no calls to other cells. Cells are usually identical and built from the same IaC, often one per account or per cluster.
- **Partition key.** What decides which cell owns a request: tenant ID, customer ID, or account ID. It has to be present on (or derivable from) every request.
- **Cell router.** The thinnest possible layer that looks up the partition key and forwards the request. It must be simpler and more reliable than anything behind it, since it is the one shared component. Keep the mapping cached locally so the router keeps working if the mapping store is down (static stability).
- **Placement / control plane.** Assigns new customers to cells, moves customers between cells, and creates new cells. It runs out of the request path, so its failure stops onboarding and migrations, not traffic.

**Sizing cells.** Set a maximum cell size you have load-tested, and add cells rather than growing past it. Smaller cells mean a smaller blast radius and cheaper tests but more overhead per customer. Very large tenants may need a dedicated cell.

**Deploying cell by cell.** Cells turn progressive delivery into a structural property. Release to a canary cell (often internal or low-value tenants), bake, then roll out in waves of cells, with automatic halt on alarms. A bad change can then only reach the cells already in the wave.

**Related techniques**

- **Shuffle sharding** assigns each customer to a random _combination_ of a few workers out of many. Two customers are unlikely to share the same combination, so a poison customer takes out only its own shard combination.
- **Bulkheads** are the same idea inside one service: separate thread pools or connection pools per dependency or tenant class.

**Trade-offs.** Anything that needs all customers at once - global search, analytics, billing roll-ups - has to be built as a separate system fed from every cell. Migrating a customer between cells is a data-migration project. N cells cost more than one shared stack, because each cell keeps its own headroom. And the router is a new single point of failure, so it needs its own multi-AZ and multi-region design. Cells pay off at large scale or with strict tenant isolation needs, not for a small product.

## Example

```text
             ┌──────────── cell router (stateless, mapping cached locally) ────────────┐
request ──▶  │  tenant_id = acme  ──▶ lookup ──▶ cell-03                               │
             └───────┬──────────────────────┬─────────────────────┬────────────────────┘
                     ▼                      ▼                     ▼
               cell-01 (canary)        cell-02                cell-03
               ALB + app + DB          ALB + app + DB         ALB + app + DB
               tenants: internal       tenants: 1-400         tenants: 401-800

A bad deploy in wave 1 (cell-01) never reaches cell-02/03.
A noisy tenant in cell-03 degrades 1/3 of customers, not all of them.
```

```python
# A minimal, statically stable cell router lookup: explicit mapping first, hash as fallback.
import hashlib

CELLS = ["cell-01", "cell-02", "cell-03"]
PINNED = {"acme": "cell-03", "bigcorp": "cell-02"}   # placement decisions, cached locally

def cell_for(tenant_id: str) -> str:
    if tenant_id in PINNED:                          # migrations update this table
        return PINNED[tenant_id]
    h = int.from_bytes(hashlib.sha256(tenant_id.encode()).digest()[:8], "big")
    return CELLS[h % len(CELLS)]                     # new tenants: deterministic spread

print(cell_for("acme"), cell_for("tenant-7781"))
```

Hashing alone would move tenants whenever a cell is added, which is why real routers persist each tenant's assignment once it is placed and use the hash only to choose a cell for new tenants.

## Interview tips

- Start with the failure it addresses: correlated failures from changes and bad inputs, which multi-AZ redundancy does not contain.
- Name the parts - cells, partition key, thin router, out-of-band placement - and say the router must be the simplest, most reliable piece.
- Connect it to deployment safety: rolling out cell by cell limits a bad release to one wave.
- Mention shuffle sharding as the related technique for isolating noisy or poison tenants.
- Be honest about the costs: cross-cell queries, tenant migration, duplicated headroom, and a router that needs its own HA design. Say when it is not worth it.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
