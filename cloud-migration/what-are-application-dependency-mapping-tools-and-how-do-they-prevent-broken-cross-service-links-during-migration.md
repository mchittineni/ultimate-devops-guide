---
title: "What are Application Dependency Mapping tools and how do they prevent broken cross-service links during migration?"
id: 697
category: "Cloud Migration"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - cloud-migration
  - discovery
  - dependency-mapping
  - architecture
quiz:
  stem: "What is the primary risk of planning cloud migration waves based on outdated corporate architecture spreadsheets rather than automated dependency discovery?"
  options:
    - "Cloud providers will reject the migration plan"
    - "Undocumented legacy network dependencies between servers will be severed, causing unexpected production outages when one service moves to the cloud while its dependency remains on-premise"
    - "Automated dependency discovery deletes server files"
    - "Spreadsheets consume too much memory"
  answer: 2
  explanation: "Architecture diagrams are notoriously stale. Automated discovery maps live network sockets, identifying hidden cross-server dependencies so tightly coupled systems can be migrated together."
---

# What are Application Dependency Mapping tools and how do they prevent broken cross-service links during migration?

**Short answer:** Application Dependency Mapping tools inspect running network connections and process sockets across enterprise servers to discover hidden, unrecorded dependencies (databases, legacy mainframes, authentication servers) before migration waves are planned.

## Detail

In data centres with 10-20 years of history, nobody has an accurate architecture diagram. Migrating "App A" frequently breaks "App B" because an undocumented batch script on App B queries App A's database over a hard-coded private IP, or because a licence server, LDAP directory, or file share was assumed rather than recorded.

### How discovery tools work

Tools such as **AWS Transform** (which took over from AWS Application Discovery Service and Migration Hub for new customers in late 2025), **Azure Migrate** (agentless dependency analysis), **Google Migration Center**, and third parties like Device42, Dynatrace, or ServiceNow Discovery collect data in three ways:

1. **Network flow analysis** - agents, hypervisor data (vCenter), or NetFlow/VPC-flow-style data record every TCP/UDP connection between hosts and ports over time.
2. **Process binding** - agents map each socket to the process that owns it (`java`, `mysqld`, `nginx`), so "10.1.4.7:5432" becomes "the orders app talks to the reporting database".
3. **Grouping into move groups** - servers that communicate continuously are grouped into the **same migration wave**, so a chatty database is not stranded on-premises while its application moves and suddenly pays 20-50 ms per query across a WAN link (which, over hundreds of queries per request, is an outage).

The output is a dependency graph that drives wave planning, firewall and security-group rules for the target, hybrid connectivity sizing, and the list of IP allow-lists that must be updated at cutover.

### Limitations

- Discovery sees only what happens **during the collection window**: a quarterly or year-end job can be missed, so collect for weeks and cover the business calendar.
- It sees connections, not **meaning**: it cannot tell a critical dependency from a stale monitoring probe, so application owners still review the map.
- Dependencies outside the network path - shared file shares mounted by hostname, DNS names embedded in config, SaaS integrations reached through a proxy, scheduled FTP drops - are easy to miss.
- Agents need change approvals on every server, which is often the slowest part of discovery; agentless collection is faster but shallower.

## Example

```bash
# Poor man's dependency mapping on one Linux server: who is connected to whom, by process.
sudo ss -tnpH state established \
  | awk '{print $4, $5, $6}' \
  | sed -E 's/users:\(\("([^"]+)".*/\1/' \
  | sort | uniq -c | sort -rn | head
#  42 10.1.4.7:8080   10.1.9.20:51544  java      <- inbound from the web tier
#  17 10.1.4.7:41822  10.1.6.3:5432    java      <- orders DB (same wave!)
#   3 10.1.4.7:50122  10.9.0.8:1414    java      <- mainframe MQ: undocumented, stays on-prem
#   1 10.1.4.7:39988  10.1.2.2:636     sssd      <- LDAP: needs a hybrid path
```

```text
Move group derived from the flow data (6 weeks of collection)

wave 2  orders-web (x4) -> orders-app (x4) -> orders-db (x2)     chatty: move together
        dependency kept on-prem: mainframe MQ (latency budget 10 ms -> Direct Connect)
        firewall rules generated: 443 in, 5432 app->db, 1414 app->onprem, 636 app->LDAP
```

## Interview tips

- Lead with the failure mode: undocumented dependencies break when one side moves and the other does not.
- Explain the mechanism - flow data plus process binding - and why interviews and spreadsheets are not enough.
- Say how the output is used: move groups, firewall rules, hybrid link sizing, and cutover allow-lists.
- Be honest about limits: the collection window, periodic jobs, and non-network dependencies.
- Mention current tooling (AWS Transform, Azure Migrate, Google Migration Center) rather than retired names.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
