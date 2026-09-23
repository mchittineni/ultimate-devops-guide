---
title: "How do you manage relational database connections in serverless functions without port exhaustion?"
id: 657
category: "Serverless Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - serverless
  - databases
  - rds-proxy
  - lambda
  - connection-pooling
quiz:
  stem: "Why does a sudden traffic surge in an AWS Lambda function connecting directly to a standard PostgreSQL RDS instance frequently crash the database?"
  options:
    - "PostgreSQL cannot run inside an Amazon VPC"
    - "Each concurrent Lambda microVM opens a separate TCP database connection, quickly exceeding PostgreSQL's `max_connections` limit"
    - "Lambda functions automatically delete SQL tables on startup"
    - "PostgreSQL does not support JSON data"
  answer: 2
  explanation: "Because Lambda functions run in independent isolated containers, scaling to 1,000 concurrent invocations attempts to open 1,000 direct database connections, exhausting database memory and connection limits."
---

# How do you manage relational database connections in serverless functions without port exhaustion?

**Short answer:** Each concurrent function instance (on Lambda, each execution environment) holds its own connection, so a burst to 2,000 concurrent executions means up to 2,000 connections - far beyond what PostgreSQL or MySQL can serve, since each connection costs server memory and a process or thread. Fix it in layers: **reuse one connection per execution environment** (open it outside the handler), **cap concurrency** to what the database can absorb, put a **connection pooler** such as RDS Proxy or PgBouncer between the functions and the database, or use a **connectionless interface** (the RDS Data API, or HTTP drivers from serverless Postgres providers). A pooler adds a hop and has its own limits, so it complements concurrency control rather than replacing it.

## Detail

**Why it breaks.** A traditional app runs a few servers with a pool of, say, 20 connections each. Serverless inverts that: many small, short-lived instances, each wanting its own connection, created in bursts. The database hits `max_connections` (`FATAL: sorry, too many clients already` in PostgreSQL), or runs out of memory first; clients see timeouts, and retries make it worse. "Port exhaustion" on the client side is rarer, but connection churn - opening and closing a TLS connection per invocation - wastes CPU on both sides.

**The controls, in order**

1. **One connection per execution environment, reused.** Create the client in global scope, not in the handler; keep the pool size at 1 because an environment only handles one request at a time on Lambda. Reconnect lazily if the connection was dropped while the environment was frozen.
2. **Cap concurrency.** Reserved concurrency on the function (or `MaximumConcurrency` on an SQS event source mapping) is a hard ceiling on connections; putting a queue in front turns bursts into a steady flow the database can handle.
3. **Pool centrally.**
   - **RDS Proxy** - a managed pooler for RDS and Aurora (PostgreSQL, MySQL, SQL Server) that multiplexes many client connections onto fewer database connections, supports IAM authentication and Secrets Manager credentials, and speeds up failover. Watch for **session pinning**: session-level state (temporary tables, `SET` statements, some prepared statements) pins a client to one backend connection and defeats multiplexing - the `DatabaseConnectionsCurrentlySessionPinned` metric shows it.
   - **PgBouncer** (self-managed, or built into some providers) in transaction mode gives the same multiplexing with more control.
4. **Go connectionless where it fits.** The RDS **Data API** (Aurora PostgreSQL and MySQL, Serverless v2 and provisioned) runs SQL over HTTPS with IAM auth, so there is no connection to manage - at the cost of per-call latency and API limits. Serverless Postgres providers (Neon, Supabase) offer HTTP or WebSocket drivers and built-in poolers for the same reason. Aurora DSQL and DynamoDB avoid the problem by design, with different data models and trade-offs.

**Other knobs:** keep transactions short (a pooler in transaction mode reuses the connection only after commit), set statement timeouts so a slow query cannot hold a connection for the function's whole timeout, and size `max_connections` alongside instance memory.

## Example

```python
# Lambda + RDS Proxy (PostgreSQL) with IAM auth: one reused connection per environment
import os, boto3, psycopg

HOST, DB, USER = os.environ["PROXY_ENDPOINT"], os.environ["DB_NAME"], os.environ["DB_USER"]
_rds = boto3.client("rds")
_conn = None

def _connect():
    token = _rds.generate_db_auth_token(DBHostname=HOST, Port=5432, DBUsername=USER)
    # statement_timeout is set on the DB role (ALTER ROLE ... SET statement_timeout = '5s'),
    # not per session - session-level SETs would pin the proxy connection
    return psycopg.connect(host=HOST, dbname=DB, user=USER, password=token,
                           sslmode="require", connect_timeout=5)

def handler(event, context):
    global _conn
    if _conn is None or _conn.closed:
        _conn = _connect()                   # only on cold start or after a dropped connection
    with _conn.transaction():                # short transaction -> proxy can reuse the backend
        row = _conn.execute("SELECT status FROM orders WHERE id = %s",
                            (event["orderId"],)).fetchone()
    return {"status": row[0] if row else None}
```

```yaml
# SAM: cap the connections this function can ever open
OrdersReader:
  Type: AWS::Serverless::Function
  Properties:
    Runtime: python3.13
    Handler: app.handler
    ReservedConcurrentExecutions: 100 # <= what the proxy/database is sized for
```

## Interview tips

- Do the arithmetic: concurrent executions roughly equal connections, and databases have hard connection and memory limits.
- Give the layered answer - reuse per environment, cap concurrency, pool with RDS Proxy or PgBouncer, or go connectionless with the Data API.
- Mention RDS Proxy session pinning; it is the detail that shows you have run it.
- Note that a queue in front of the function is often the simplest way to protect the database from bursts.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?]] (`#539`): [What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?](../cicd/what-are-slsa-supply-chain-levels-for-software-artifacts-frameworks-and-how-do-they-verify-build-integrity.md)
- [[What is the difference between Docker Image and Docker Container?]] (`#7`): [What is the difference between Docker Image and Docker Container?](../docker/what-is-the-difference-between-docker-image-and-docker-container.md)
- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
