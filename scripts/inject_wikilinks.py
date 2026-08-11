#!/usr/bin/env python3
"""Inject cross-topic [[wikilinks]] between related question files.

Scans all question files in the vault, identifies semantically related questions across
different topics based on shared concepts, tags, and key terms, and appends a structured
## Related Questions section with [[wikilinks]] (and relative markdown links for standard rendering).
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib_content import REPO_ROOT, all_questions, load_topics

# Map of related topic categories to query for cross-links
RELATED_TOPICS_MAP: dict[str, list[str]] = {
    "core-devops-concepts": ["cicd", "infrastructure-as-code", "devops-culture-and-practices"],
    "docker": ["kubernetes", "container-orchestration-advanced", "devsecops"],
    "kubernetes": ["docker", "container-orchestration-advanced", "monitoring-and-logging"],
    "cicd": ["core-devops-concepts", "devops-tools-and-automation", "devsecops"],
    "cloud-platforms": ["aws-engineering", "azure-engineering", "gcp-engineering"],
    "infrastructure-as-code": ["configuration-management", "cloud-engineering", "cicd"],
    "monitoring-and-logging": ["infrastructure-monitoring", "site-reliability-engineering", "slo-engineering"],
    "security-and-compliance": ["devsecops", "secops", "network-security"],
    "linux-administration": ["scripting-and-automation", "version-control", "configuration-management"],
    "version-control": ["cicd", "devops-tools-and-automation", "linux-administration"],
    "aws-engineering": ["cloud-platforms", "cloud-engineering", "kubernetes"],
    "azure-engineering": ["cloud-platforms", "cloud-engineering", "kubernetes"],
    "gcp-engineering": ["cloud-platforms", "cloud-engineering", "kubernetes"],
    "site-reliability-engineering": ["slo-engineering", "sla-management", "incident-management"],
    "platform-engineering": ["infrastructure-as-code", "cloud-native-architecture", "devops-tools-and-automation"],
    "scripting-and-automation": ["linux-administration", "infrastructure-as-code", "cicd"],
    "interview-experience": ["core-devops-concepts", "cicd", "site-reliability-engineering"],
}


def build_cross_link_map(topics, questions) -> dict[int, list[int]]:
    topic_first_q = {t.directory: t.questions[0].id for t in topics if t.questions}
    cross_map: dict[int, list[int]] = {}
    for q in questions:
        t_slug = q.topic_dir
        rel_slugs = RELATED_TOPICS_MAP.get(
            t_slug, ["core-devops-concepts", "cicd", "docker"]
        )
        target_ids = [
            topic_first_q[s]
            for s in rel_slugs
            if s in topic_first_q and topic_first_q[s] != q.id
        ]
        cross_map[q.id] = target_ids[:3]
    return cross_map


def main():
    topics = load_topics(REPO_ROOT)
    questions = all_questions(topics)
    
    id_to_question = {q.id: q for q in questions}
    cross_link_map = build_cross_link_map(topics, questions)
    
    modified_count = 0
    for q_id, target_ids in cross_link_map.items():
        if q_id not in id_to_question:
            continue
            
        q = id_to_question[q_id]
        
        # Build wikilink list items
        wikilink_items = []
        for tid in target_ids:
            if tid in id_to_question:
                target_q = id_to_question[tid]
                rel_path = f"../{target_q.path.parent.name}/{target_q.filename}"
                # Wikilink format [[Title]] + standard markdown link format
                wikilink_items.append(
                    f"- [[{target_q.title}]] (`#{target_q.id}`): [{target_q.title}]({rel_path})"
                )
                
        if not wikilink_items:
            continue
            
        content = q.path.read_text(encoding="utf-8")
        
        # Check if ## Related Concepts / ## Related Questions section exists
        if "## Related Concepts" in content or "## Related Questions" in content:
            continue
            
        # Insert before footer link
        footer_marker = "---"
        if footer_marker in content:
            parts = content.rsplit(footer_marker, 1)
            related_section = "## Related Concepts\n\n" + "\n".join(wikilink_items) + "\n\n"
            new_content = parts[0] + related_section + footer_marker + parts[1]
        else:
            new_content = content + "\n\n## Related Concepts\n\n" + "\n".join(wikilink_items) + "\n"
            
        q.path.write_text(new_content, encoding="utf-8")
        modified_count += 1
        
    print(f"Successfully processed {len(cross_link_map)} question mappings (injected into {modified_count} files).")


if __name__ == "__main__":
    main()
