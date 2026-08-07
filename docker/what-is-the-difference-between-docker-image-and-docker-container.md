---
title: "What is the difference between Docker Image and Docker Container?"
id: 7
category: "Docker"
difficulty: "Beginner"
tags:
  - devops
  - docker
  - interview-questions
---

# What is the difference between Docker Image and Docker Container?

**Short answer:** An image is an immutable, read-only template built from a Dockerfile; a container is a running instance of that image with a thin writable layer on top. Image is to container what a class is to an object, or a binary to a process.

## Detail

An **image** is a stack of read-only layers plus metadata (entrypoint, environment, exposed ports). Each Dockerfile instruction that changes the filesystem creates a layer, identified by a content digest. Layers are shared: ten containers from the same image consume the image's disk space once.

A **container** adds a writable layer on top of those read-only layers, using a copy-on-write filesystem. Writes inside a running container land in this layer, and it is deleted when the container is removed - which is why anything you need to keep belongs in a volume or an external datastore.

|           | Image                         | Container                          |
| --------- | ----------------------------- | ---------------------------------- |
| State     | Immutable                     | Mutable (writable layer)           |
| Lifecycle | Built, pushed, pulled         | Created, started, stopped, removed |
| Storage   | Shared read-only layers       | Own thin writable layer            |
| Command   | `docker build`, `docker pull` | `docker run`, `docker stop`        |

## Example

```bash
docker images                      # list images (templates)
docker ps -a                       # list containers (instances)
docker run -d --name a nginx:1.27  # two containers...
docker run -d --name b nginx:1.27  # ...one shared image on disk
docker diff a                      # inspect a container's writable layer
```

## Interview tips

- Use the class/object analogy, then immediately back it with copy-on-write layers.
- Mention that data in the writable layer is lost on `docker rm` - it leads naturally into volumes.
- A follow-up is often "why are my images so large?" - answer with layer caching and multi-stage builds.

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
