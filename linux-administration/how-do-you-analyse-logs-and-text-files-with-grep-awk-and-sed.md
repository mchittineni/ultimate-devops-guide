---
title: "How do you analyse logs and text files with grep, awk, and sed?"
id: 265
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - linux-administration
  - interview-questions
---

# How do you analyse logs and text files with grep, awk, and sed?

**Short answer:** `grep` selects lines that match a pattern, `awk` splits each line into fields and operates on them, and `sed` edits a stream line by line. The workflow is almost always the same pipeline: filter with `grep`, extract or aggregate columns with `awk`, transform text with `sed`, then `sort | uniq -c | sort -rn` to rank the result.

## Detail

**These three appear in more DevOps interviews than any other Linux topic**, usually as a live "how would you find X in this log" question. You are not expected to know every flag - you are expected to reach for the right tool without hesitating.

**`grep` - find the lines.** The flags that matter in practice:

| Flag                     | Effect                                                        |
| ------------------------ | ------------------------------------------------------------- |
| `-i`                     | Case-insensitive                                              |
| `-v`                     | Invert - lines that do _not_ match                            |
| `-r`                     | Recurse through directories                                   |
| `-c`                     | Count matching lines instead of printing them                 |
| `-n`                     | Show line numbers                                             |
| `-E`                     | Extended regex, so alternation works: `grep -E 'warn\|error'` |
| `-A n` / `-B n` / `-C n` | n lines After / Before / around each match                    |

`-C 5` around a stack trace is the flag that actually solves incidents. `grep -c` counting errors per minute is how you decide whether something is a blip or a trend.

**`awk` - work with columns.** `awk` splits each line on whitespace (or on `-F<delimiter>`) into `$1`, `$2`, … with `$0` as the whole line and `NF` as the field count. The structure is `pattern { action }`, plus optional `BEGIN` and `END` blocks. Anything involving "sum the bytes", "average the response time", or "count by status code" is an `awk` job, not a `grep` one.

**`sed` - transform the stream.** Overwhelmingly used as `sed 's/old/new/g'`. Also worth knowing: `sed -n '10,20p'` to print a line range, `sed -i` to edit in place (on macOS/BSD it needs an argument: `sed -i ''`), and `sed '/pattern/d'` to delete matching lines. In CI, `sed -i` is the common way to stamp an image tag into a manifest - though `yq` is safer for YAML.

**The reading-large-files questions** come up constantly, because "the log is 40 GB" is a real constraint:

- `tail -n 100 file` - last 100 lines. `tail -f` (or `tail -F`, which survives rotation) to follow live.
- `head -n 50 file` - first 50.
- `sed -n '4500,4600p' file` - a specific range without loading the whole file.
- `less +F file` - follow like `tail -f` but with search and scrollback.
- `zgrep` / `zcat` - search compressed rotated logs without decompressing them to disk.
- Never `cat` a multi-gigabyte file into a terminal.

**The counting idiom** is worth memorising as a unit, because half of all log analysis is this one line:

```bash
... | sort | uniq -c | sort -rn | head
```

`uniq -c` only collapses _adjacent_ duplicates, which is why the first `sort` is mandatory - forgetting it is the classic bug.

**Other tools that belong in the answer:** `cut` for simple fixed-delimiter fields, `tr` for character translation and squeezing, `wc -l` for counting, `xargs` for feeding results into another command, and `jq` once logs are JSON - which, for anything structured, is the right answer rather than `awk`.

## Example

```bash
# Top 10 IPs hitting the site, classic access-log analysis
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Count requests by HTTP status code
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# 5xx responses only, with the URL and the response time (field 11 here)
awk '$9 ~ /^5/ {print $9, $7, $11}' /var/log/nginx/access.log | head -20

# Average and max response time, computed in one pass
awk '{sum+=$11; if($11>max) max=$11} END {printf "avg=%.3fs max=%.3fs n=%d\n", sum/NR, max, NR}' \
  /var/log/nginx/access.log

# Total bytes served, in MB
awk '{sum+=$10} END {print sum/1024/1024 " MB"}' /var/log/nginx/access.log

# Errors in a time window, with 5 lines of context around each
grep -C 5 'ERROR' app.log | grep -A5 '2026-08-07T14:'

# Errors per minute - is this a spike or a steady rate?
grep ERROR app.log | awk '{print substr($1,1,16)}' | uniq -c

# Search rotated, compressed logs
zgrep -c 'OutOfMemory' /var/log/app/*.log.gz

# Field extraction from a colon-delimited file
awk -F: '$3 >= 1000 {print $1, $6}' /etc/passwd   # human users and their homes

# In-place substitution: stamp an image tag into a manifest
sed -i 's|image: myapp:.*|image: myapp:1.4.0|' k8s/deployment.yaml

# Print a specific line range from a huge file without reading it all
sed -n '4500,4600p' huge.log

# JSON logs: use jq, not awk
kubectl logs deploy/api --since=15m | jq -r 'select(.level=="error") | .msg' | sort | uniq -c | sort -rn
```

## Interview tips

- "How do you print the last 15 lines of a file?" and "how do you read a large log without opening it fully?" are asked verbatim. Answer `tail -n 15` and `tail -f`/`less +F`, and add that you would never `cat` a huge file.
- Have the top-N idiom ready as one fluent line: `awk '{print $1}' | sort | uniq -c | sort -rn | head`. Explain why the first `sort` is required.
- Draw the division of labour clearly: grep selects lines, awk works with fields, sed transforms text. That sentence alone answers "what is the difference between them?"
- Be ready for a live scenario - "find the top 5 URLs returning 500s in this access log." Talk through the pipeline as you build it rather than producing a silent one-liner.
- Mention `jq` for structured logs. Reaching for `awk` on JSON when `jq` exists reads as dated.
- Know that `sed -i` differs between GNU and BSD/macOS. It is a small detail that signals real command-line time.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
