---
title: "What is the difference between hard links and symbolic (soft) links in Linux?"
id: 571
category: "Linux Administration"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - linux
  - filesystem
  - symlinks
  - hardlinks
quiz:
  stem: "What happens to the target data if the original file is deleted after creating a hard link to it in Linux?"
  options:
    - "The hard link breaks and the data is lost"
    - "The data remains intact and fully readable via the hard link because the inode link count is still greater than zero"
    - "The Linux kernel reboots to repair filesystem integrity"
    - "The hard link automatically converts into a symbolic link"
  answer: 2
  explanation: "Deleting a file decrements the inode's reference count. Since the hard link points directly to the inode, the data is preserved on disk until all hard links are unlinked."
---

# What is the difference between hard links and symbolic (soft) links in Linux?

**Short answer:** A hard link is an additional directory entry pointing directly to an existing inode on the same filesystem; a symbolic link is a separate file with its own inode containing the path string to another file, capable of spanning across filesystems.

## Detail

Understanding links prevents accidental file deletion and data loss:

| Dimension           | Hard Link (`ln file link`)                                        | Symbolic Link (`ln -s file link`)                              |
| ------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------- |
| Inode Number        | Shares the **exact same inode number** as the source file         | Has its **own distinct inode number**                          |
| Cross-Filesystem    | **No** (inodes are local to a specific filesystem partition)      | **Yes** (references a path string; can cross disks/partitions) |
| Target Deleted      | File content remains accessible until all hard links are unlinked | Becomes a **broken dangling link**                             |
| Linking Directories | Prohibited (prevents circular loops in directory trees)           | Allowed                                                        |
| File Size           | Reports the same size as the underlying data                      | Size equals the length of the target path string               |

### How File Deletion Works

When you run `rm myfile`, you do not delete the file; you call `unlink()`. The kernel decrements the inode's link count (`i_nlink`). Only when the link count reaches 0 AND no running process has an open file descriptor pointing to it does the kernel free the disk blocks.

## Example

```bash
echo data > file.txt
ln file.txt hard.txt          # second name, same inode
ln -s file.txt soft.txt       # new inode containing the path "file.txt"
ls -li                        # file.txt and hard.txt share an inode number; link count is 2
rm file.txt
cat hard.txt                  # "data" - the inode still has one name
cat soft.txt                  # No such file or directory - the symlink now dangles

# Space not freed after rm? A process still holds the deleted file open
lsof +L1
```

## Interview tips

- Lead with the mechanism: a hard link is another directory entry for the same inode; a symlink is its own small file whose content is a path, resolved at access time.
- The restrictions follow from that: hard links cannot cross filesystems (inode numbers are per filesystem) or point at directories (to prevent loops), while symlinks can do both but break when the target moves.
- Tie deletion to `unlink()`: data blocks are freed only when the link count reaches zero **and** no process has the file open - the reason `df` and `du` disagree after deleting a busy log file.
- Give a real use of each: symlinks for atomic release switching (`current -> 1.9.0`), hard links for space-efficient backups (`rsync --link-dest`).
- For a fuller treatment, see [what is the difference between a hard link and a soft link](./what-is-the-difference-between-a-hard-link-and-a-soft-link.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)
- [[What do you use Python for as a DevOps engineer?]] (`#267`): [What do you use Python for as a DevOps engineer?](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md)
- [[When do you use Bash and when do you use Python?]] (`#301`): [When do you use Bash and when do you use Python?](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
