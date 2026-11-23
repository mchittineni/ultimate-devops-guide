---
title: "Can you delete a Docker image that a container is still using, and what happens to that container?"
id: 792
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - docker
  - images
  - disk-cleanup
quiz:
  stem: "You run `docker rmi -f myapp:1.4` while a running container was created from that image. What happens?"
  options:
    - "The container is stopped and deleted along with the image"
    - "The tag is removed, the image shows as `<none>`, and its layers stay because the container still needs them"
    - "The image layers are deleted and the container crashes on its next disk read"
    - "Docker refuses the command because `-f` cannot be used on tagged images"
  answer: 2
  explanation: "A container references its image by ID, not by tag. Force-removing the tag only untags the image; Docker keeps the layers while any container depends on them, so no space is freed and the container keeps running."
---

# Can you delete a Docker image that a container is still using, and what happens to that container?

**Short answer:** Not really. A plain `docker rmi` fails while **any** container, running or stopped, was created from the image. With `-f` against a **tag**, Docker only removes the tag: the image becomes `<none>:<none>` and its layers stay on disk, because the container's filesystem is built on them. With `-f` against the **image ID** while a running container uses it, Docker refuses outright. The container is unaffected either way, and even after it is stopped it can be started again with `docker start`. What you lose is the ability to **recreate** it from that tag without pulling the image again.

## Detail

**Why the image cannot really go.** A container's root filesystem is a writable layer stacked on the image's read-only layers. The container records its image by **ID** (`sha256:...`), not by tag. Tags are just names pointing at that ID. Docker will not delete layers that a container depends on, because the container could not run or start without them.

**What each command does.**

| Command                                           | Container using the image | Result                                                                                 |
| ------------------------------------------------- | ------------------------- | -------------------------------------------------------------------------------------- |
| `docker rmi myapp:1.4`                            | running or stopped        | Fails with a conflict: a container is using the referenced image                       |
| `docker rmi -f myapp:1.4`                         | running or stopped        | Tag removed; image remains as `<none>:<none>`; no space freed                          |
| `docker rmi -f <image-id>`                        | running                   | Refused: the image is being used by a running container and cannot be forced           |
| `docker rm <container>` then `docker image prune` | none left                 | The untagged image is now dangling and unused, so prune deletes it and frees the space |

The exact error wording differs between Docker Engine versions and between the classic and containerd image stores, but the rule is the same: layers in use are kept.

**Can the stopped container start again?** Yes. `docker start` and `docker restart` reuse the existing container, which still has its config, its writable layer, and a reference to the image ID whose layers are still present. The application comes back as before.

**What does break.** Anything that **creates a new container** from the tag: `docker run myapp:1.4`, `docker compose up --force-recreate`, or a restart policy on a new host. The tag no longer exists locally, so Docker tries to pull it from the registry, which fails if the registry no longer has it or the host is offline. That is the real risk, and it is why deployments should reference images by **digest** and keep them in a registry with sensible retention.

**Kubernetes behaves similarly.** The kubelet's image garbage collection never removes images used by running containers. A new Pod pulls the image again according to `imagePullPolicy`.

**How to actually free disk space.** Stop and remove the containers you no longer need, then prune:

- `docker image prune` removes dangling images not used by any container.
- `docker image prune -a` also removes tagged images that no container uses.
- `docker builder prune` clears the BuildKit cache, which is often the largest consumer on CI hosts.
- `docker system df` shows how much space images, containers, volumes, and build cache use.

## Example

```bash
docker run -d --name web nginx:1.27
docker rmi nginx:1.27
# Error: conflict: unable to remove repository reference "nginx:1.27" (must force) - container ... is using its referenced image ...

docker rmi -f nginx:1.27            # prints "Untagged: nginx:1.27" and nothing is deleted
docker images                       # the image now appears as <none> <none>
docker inspect web --format '{{.Image}}'    # the container still points at sha256:...

docker stop web && docker start web         # starts normally: the layers are still there
docker run -d nginx:1.27                    # a NEW container needs the tag, so Docker pulls it again

docker rm -f web && docker image prune -f   # now the old image is actually removed
docker system df
```

## Interview tips

- The common wrong answer is "no, you must stop the container first." Stopping is not enough: a stopped container still blocks a normal `docker rmi`. You must remove the container, or use `-f`, which only untags.
- The second common wrong answer is "after a force delete, the container cannot be restarted." It can, because the layers are kept. What fails is creating a new container from the missing tag.
- Explain that containers reference images by ID and that tags are just names; that single fact answers most follow-ups.
- If asked about disk cleanup, go to `docker system df`, `docker image prune -a`, and `docker builder prune`, not `rmi -f`.
- Mention digest pinning as the way to make recreation predictable.

**Telling it as a STAR story** (an adaptable example)

- **Situation:** A CI build host ran out of disk, and a teammate planned to force-remove old images while some services built from them were still running.
- **Task:** Free space safely and explain what force removal would actually do.
- **Action:** I used `docker ps -a --filter ancestor=<image>` to see which containers used each image and showed that `rmi -f` on a tag only untags the image and frees nothing. I removed the containers that were genuinely obsolete, ran `docker image prune -a --filter until=168h` and `docker builder prune`, and checked the result with `docker system df`. I also confirmed the running services' images still existed in the registry by digest.
- **Result:** We recovered tens of gigabytes without touching a running service and added a scheduled prune job so the host did not fill up again.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck in ImagePullBackOff?]] (`#751`): [How do you troubleshoot a Pod stuck in ImagePullBackOff?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-imagepullbackoff.md)
- [[What is Kubernetes?]] (`#11`): [What is Kubernetes?](../kubernetes/what-is-kubernetes.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
