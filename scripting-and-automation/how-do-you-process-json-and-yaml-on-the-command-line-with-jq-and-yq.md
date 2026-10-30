---
title: "How do you process JSON and YAML on the command line with jq and yq?"
id: 780
category: "Scripting and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - scripting-and-automation
  - interview-questions
quiz:
  stem: "Why is `jq -r '.items[].metadata.name'` preferred over `grep '\"name\"' | cut -d'\"' -f4` for extracting Kubernetes resource names?"
  options:
    - "jq is faster on files under 1 KB"
    - "jq parses the JSON structure, so it is unaffected by formatting, key order, nesting, or a 'name' key appearing elsewhere"
    - "grep cannot read JSON files"
    - "cut only works on CSV"
  answer: 2
  explanation: "Text tools match characters, not structure: a reformatted document, a nested 'name' field, or an escaped quote silently breaks them. jq addresses fields by path, so the extraction is correct by construction."
---

# How do you process JSON and YAML on the command line with jq and yq?

**Short answer:** **jq** is a small functional language for JSON: a filter such as `.items[] | select(.status.phase != "Running") | .metadata.name` walks the structure, filters, and reshapes it, and `-r` prints raw strings for the next command in the pipe. **yq** brings the same idea to YAML (and can convert between YAML, JSON, TOML, and XML), which makes it the safe way to read or edit Kubernetes manifests, Helm values, and CI files in a script instead of `sed`. The habits that matter in automation: parse structure rather than grepping text, pass shell values in with `--arg`/`--argjson` (or `env()` in yq) rather than interpolating them into the filter, use `-e` so a missing value fails the script, and know there are **two different tools called yq** - the Go one (`mikefarah/yq`, the common default) and a Python jq wrapper - with different syntax.

## Detail

### jq: the core you actually use

| Need                | Filter                                                           |
| ------------------- | ---------------------------------------------------------------- |
| A field             | `.metadata.name`                                                 |
| Every element       | `.items[]`                                                       |
| Filter              | `select(.status == "FAILED")`                                    |
| Reshape             | `{name: .metadata.name, ns: .metadata.namespace}`                |
| Default for missing | `.spec.replicas // 1`                                            |
| Optional (no error) | `.metadata.labels.app?`                                          |
| Count / aggregate   | `length`, `map(.size) \| add`, `group_by(.team)`                 |
| Keys and entries    | `keys`, `to_entries[] \| "\(.key)=\(.value)"`                    |
| Text output         | `-r` raw strings, `@tsv`, `@csv`, string interpolation `"\(.a)"` |

Pipes inside a filter (`|`) pass each result to the next expression, and a filter can produce **many** results - `.items[]` emits one value per element, which is why `[ ... ]` is needed to collect them back into an array.

### Flags that make jq safe in scripts

- `-r` - raw strings, no JSON quotes, so the output can feed `xargs` or a `while read` loop.
- `-e` - exit non-zero if the last output is `false` or `null`. Without it, `jq .missing.key` prints `null` and exits 0, and the script carries on with the string "null".
- `--arg name value` / `--argjson name 5` - pass shell variables as typed jq variables. Building the filter with string interpolation (`jq ".[] | select(.name == \"$NAME\")"`) breaks on quotes and is an injection vector.
- `-c` - one compact JSON object per line, ideal for streaming into another tool.
- `-n` with `--arg` - build JSON from scratch (a safe way to construct an API payload).
- `--slurp` / `-s` - read a stream of objects into one array; `--stream` for documents too large to load.

### yq (mikefarah, v4)

Uses jq-like expressions on YAML while preserving comments and most formatting:

- Read: `yq '.spec.template.spec.containers[0].image' deploy.yaml`
- Edit in place: `yq -i '.image.tag = strenv(TAG)' values.yaml` - `strenv`/`env` are the yq equivalent of `--arg`.
- Multi-document files: expressions apply to each document; `select(.kind == "Deployment")` targets one.
- Convert: `yq -o=json`, `yq -p=json -o=yaml`.

Check which yq you have (`yq --version`): the Python `kislyuk/yq` wraps jq and uses jq's flags exactly, while the Go version has its own operators. Scripts written for one fail on the other. Pin it in the CI image.

### When to use which tool

- Extracting a few fields from a CLI's JSON output (`kubectl`, `aws`, `gh`, `terraform show -json`) - jq. Many CLIs also have built-in query flags (`kubectl -o jsonpath`, `aws --query` JMESPath, `gh --jq`) that avoid the extra dependency.
- Editing YAML in a pipeline (bumping an image tag in a GitOps repo) - yq, not `sed`, because `sed` does not know indentation, anchors, or which `image:` key you meant. For Kubernetes manifests, `kustomize edit set image` is better still.
- Anything with loops over API pages, retries, or more than a dozen lines of jq - switch to Python, where the same logic is testable and readable.

## Example

```bash
# Pods that are not Running, as "namespace/name phase"
kubectl get pods -A -o json \
  | jq -r '.items[] | select(.status.phase != "Running")
           | "\(.metadata.namespace)/\(.metadata.name) \(.status.phase)"'

# Pass shell values safely; -e fails the script if nothing matches
NS=payments
kubectl get deploy -n "$NS" -o json \
  | jq -e --arg ns "$NS" '.items[] | select(.metadata.namespace == $ns) | .metadata.name'

# Terraform plan gate: fail CI if anything would be destroyed
terraform show -json tfplan \
  | jq -e '[.resource_changes[] | select(.change.actions | index("delete"))] | length == 0' >/dev/null \
  || { echo "plan destroys resources - needs manual approval" >&2; exit 1; }

# AWS: untagged running instances, tab-separated
aws ec2 describe-instances --filters Name=instance-state-name,Values=running \
  | jq -r '.Reservations[].Instances[]
           | select((.Tags // []) | map(.Key) | index("Owner") | not)
           | [.InstanceId, .InstanceType] | @tsv'

# Build a JSON payload without string-concatenation bugs
jq -n --arg text "Deploy of $SERVICE finished" --arg env "$ENV" \
  '{text: $text, attachments: [{fields: [{title: "env", value: $env}]}]}' \
  | curl -fsS -X POST -H 'Content-Type: application/json' --data @- "$SLACK_WEBHOOK"
```

```bash
# yq (mikefarah v4): read, edit in place, select one document, convert
yq '.image.tag' charts/api/values.yaml
TAG=1.9.0 yq -i '.image.tag = strenv(TAG)' charts/api/values.yaml
yq 'select(.kind == "Deployment") | .spec.replicas' k8s/all.yaml
yq -o=json '.' config.yaml | jq '.database'
yq --version        # confirm WHICH yq is installed before relying on its syntax
```

## Interview tips

- Say why first: text tools match characters, jq and yq match structure - so formatting, key order, and nesting cannot break the extraction.
- Show the three flags that make jq script-safe: `-r` for raw output, `-e` so a missing value fails, and `--arg` instead of interpolating shell variables into the filter.
- Use a real gate as your example - failing a pipeline when a Terraform plan contains a delete is a strong, practical answer.
- For YAML edits in CI, choose yq (or `kustomize edit`) over `sed`, and mention that two incompatible tools share the name yq, so pin the version.
- Know the boundary: a long jq program is a sign the job wants Python. See [when do you use Bash and when do you use Python](./when-do-you-use-bash-and-when-do-you-use-python.md), [what Bash scripting exercises come up in DevOps interviews](./what-bash-scripting-exercises-come-up-in-devops-interviews.md), and [analysing logs with grep, awk, and sed](../linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you schedule work with cron and systemd timers?]] (`#497`): [How do you schedule work with cron and systemd timers?](../linux-administration/how-do-you-schedule-work-with-cron-and-systemd-timers.md)
- [[How do you analyse logs and text files with grep, awk, and sed?]] (`#265`): [How do you analyse logs and text files with grep, awk, and sed?](../linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md)
- [[What is the difference between a hard link and a soft link?]] (`#494`): [What is the difference between a hard link and a soft link?](../linux-administration/what-is-the-difference-between-a-hard-link-and-a-soft-link.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scripting and Automation](./README.md) · [All topics](../README.md)
