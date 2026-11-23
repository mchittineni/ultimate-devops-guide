---
title: "How do you containerise a three-tier application with Docker and Docker Compose?"
id: 794
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - docker
  - docker-compose
  - multi-stage
  - networking
quiz:
  stem: "In a Compose file for a React frontend, a Node.js API, and MySQL, how should the database be exposed?"
  options:
    - "Publish 3306 on the host so the frontend can query it directly"
    - "Put it on a backend network shared only with the API and publish no ports for it"
    - "Put all three services on the default network and publish every port"
    - "Run MySQL inside the API container to avoid networking"
  answer: 2
  explanation: "Only the API needs the database. A separate backend network keeps the frontend from reaching it, and not publishing 3306 means nothing outside the Docker host can connect to it."
---

# How do you containerise a three-tier application with Docker and Docker Compose?

**Short answer:** One image per tier, one Compose file to run them together. The **frontend** (for example React) is built in a Node stage and served as static files by nginx using a multi-stage Dockerfile. The **API** (Node.js, Python, or similar) gets a slim, non-root image with only production dependencies. The **database** uses the official image unchanged, with a named volume for its data. Compose then puts the tiers on **separate networks** so only the API can reach the database, publishes **only the frontend port**, uses **health checks with `depends_on: condition: service_healthy`** for start order, and passes credentials as secrets rather than baking them into images.

## Detail

**Frontend.** A React build produces static HTML, JS, and CSS, so the runtime image does not need Node at all. Stage one runs `npm ci` and `npm run build`; stage two copies only the build output into an nginx image. nginx also reverse-proxies `/api` to the API service, so the browser talks to one origin and CORS problems disappear.

**API.** Start from a slim base, install with `npm ci --omit=dev` (or the equivalent for Python), copy the source after the dependency files so the dependency layer stays cached, and run as a non-root user. Read configuration from environment variables and secret files, never from files committed into the image.

**Database.** No custom Dockerfile is needed. The official MySQL image reads `MYSQL_DATABASE`, `MYSQL_USER`, and `*_FILE` variants of the password variables, and runs any `.sql` files in `/docker-entrypoint-initdb.d` on first start only (when the data directory is empty). A **named volume** on `/var/lib/mysql` keeps data across `docker compose down` and up; `down -v` deletes it.

**Networking.** Compose creates DNS names from service names, so the API connects to `db:3306` and nginx proxies to `api:3000`. Two user-defined networks give least privilege: `frontend` for web and API, `backend` for API and database. Marking `backend` as `internal: true` also stops the database from reaching the internet. Publish only the web port; never publish 3306 outside local debugging.

**Start order.** `depends_on` alone only waits for the container to start, not for MySQL to accept connections. Add a `healthcheck` to the database and use `condition: service_healthy` so the API starts once the database is ready. The API should still retry its connection, because a database can restart later too.

**Secrets.** Compose `secrets` mount files under `/run/secrets/`, which the MySQL image reads through `MYSQL_PASSWORD_FILE`. That keeps passwords out of `docker inspect` output and out of image layers.

**From Compose to production.** Compose is the right tool for local development and CI integration tests. For production the same images are built in CI, pushed to a registry, and deployed to ECS or Kubernetes, usually with a managed database (RDS, Cloud SQL, Azure Database for MySQL) replacing the MySQL container.

## Example

```dockerfile
# frontend/Dockerfile
FROM node:24-alpine AS build
WORKDIR /src
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Vite writes to dist/; Create React App writes to build/
COPY --from=build /src/dist /usr/share/nginx/html
EXPOSE 8080
```

```nginx
# frontend/nginx.conf
server {
  listen 8080;
  root /usr/share/nginx/html;
  location /api/ { proxy_pass http://api:3000; }
  location / { try_files $uri /index.html; }
}
```

```dockerfile
# api/Dockerfile
FROM node:24-slim
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY --chown=node:node . .
USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

```yaml
# compose.yaml
services:
  web:
    build: ./frontend
    ports: ["8080:8080"] # the only published port
    networks: [frontend]
    depends_on: [api]

  api:
    build: ./api
    environment:
      DB_HOST: db
      DB_NAME: shop
      DB_USER: shop
      DB_PASSWORD_FILE: /run/secrets/db_password
    secrets: [db_password]
    networks: [frontend, backend]
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://localhost:3000/healthz').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 10s
      retries: 3

  db:
    image: mysql:8.4
    environment:
      MYSQL_DATABASE: shop
      MYSQL_USER: shop
      MYSQL_PASSWORD_FILE: /run/secrets/db_password
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
    secrets: [db_password, db_root_password]
    volumes:
      - db-data:/var/lib/mysql
      - ./db/init:/docker-entrypoint-initdb.d:ro
    networks: [backend]
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "127.0.0.1", "--silent"]
      interval: 5s
      retries: 10

networks:
  frontend: {}
  backend: { internal: true } # no route out, and the web tier is not attached

volumes:
  db-data: {}

secrets:
  db_password: { file: ./secrets/db_password.txt }
  db_root_password: { file: ./secrets/db_root_password.txt }
```

```bash
docker compose up -d --build
docker compose ps                       # db should show (healthy) before api starts
docker compose exec api getent hosts db   # service names resolve through Compose DNS
docker compose down                     # keeps the db-data volume; add -v to wipe it
```

## Interview tips

- A common answer is "three images on one shared network, expose only the frontend." That is a fair start; improve it with two networks, a named volume for MySQL, health-checked start order, and secrets instead of plain environment variables.
- Say why the frontend image has no Node runtime: the multi-stage build ships only static files, which makes the image small and reduces attack surface.
- Explain that `depends_on` without a health condition does not wait for readiness, and that the app should retry connections anyway.
- Expect "how would you run this in production?" Answer with CI-built images in a registry, ECS or Kubernetes for orchestration, and a managed database rather than a MySQL container.
- Mention that `.sql` files in `/docker-entrypoint-initdb.d` run only when the data volume is empty, which surprises people who expect them on every start.

**Telling it as a STAR story** (an adaptable example)

- **Situation:** A three-tier app (React, Node.js API, MySQL) only ran on developers' laptops after a long manual setup.
- **Task:** Containerise it so it ran identically locally and in CI and could later move to a managed platform.
- **Action:** I wrote a multi-stage frontend Dockerfile that served the build through unprivileged nginx and proxied `/api`, a slim non-root API image, and a Compose file with the official MySQL image, a named volume, seed scripts, and file-based secrets. Two networks kept the database reachable only from the API, and a `mysqladmin ping` health check gated the API's start.
- **Result:** New developers went from most of a day of setup to `docker compose up`, CI ran integration tests against the same stack, and the images later moved to Kubernetes with a managed database in place of the MySQL container.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does the Kubernetes Gateway API evolve beyond standard Ingress resources?]] (`#520`): [How does the Kubernetes Gateway API evolve beyond standard Ingress resources?](../kubernetes/how-does-the-kubernetes-gateway-api-evolve-beyond-standard-ingress-resources.md)
- [[How do you troubleshoot a Pod stuck in ImagePullBackOff?]] (`#751`): [How do you troubleshoot a Pod stuck in ImagePullBackOff?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-imagepullbackoff.md)
- [[What is the difference between Service types ClusterIP, NodePort, LoadBalancer, and ExternalName?]] (`#531`): [What is the difference between Service types ClusterIP, NodePort, LoadBalancer, and ExternalName?](../kubernetes/what-is-the-difference-between-service-types-clusterip-nodeport-loadbalancer-and-externalname.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
