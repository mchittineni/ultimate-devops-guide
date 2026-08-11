#!/usr/bin/env python3
"""Inject cross-topic [[wikilinks]] between related question files.

Scans all question files in the vault, identifies semantically related questions across
different topics based on shared concepts, tags, and key terms, and appends a structured
## Related Questions section with [[wikilinks]] (and relative markdown links for standard rendering).
"""

from __future__ import annotations

import re
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
    """Build cross-links based on semantic metadata: tags, category, and shared terms.

    Validates complete coverage and fails loudly on unmapped topics or missing targets.
    """
    # Build topic -> questions lookup
    topic_to_questions = {t.directory: t.questions for t in topics}

    # Validate all RELATED_TOPICS_MAP source topics exist
    unmapped_sources = set()
    for source_topic in RELATED_TOPICS_MAP.keys():
        if source_topic not in topic_to_questions or not topic_to_questions[source_topic]:
            unmapped_sources.add(source_topic)

    # Validate all target topics in RELATED_TOPICS_MAP exist
    unmapped_targets = set()
    for source_topic, target_list in RELATED_TOPICS_MAP.items():
        for target_topic in target_list:
            if target_topic not in topic_to_questions or not topic_to_questions[target_topic]:
                unmapped_targets.add(target_topic)

    # Fail loudly if unmapped topics are found
    if unmapped_sources or unmapped_targets:
        error_msg = "Cross-link mapping validation failed:\n"
        if unmapped_sources:
            error_msg += f"  Unmapped source topics: {sorted(unmapped_sources)}\n"
        if unmapped_targets:
            error_msg += f"  Unmapped target topics: {sorted(unmapped_targets)}\n"
        raise SystemExit(error_msg)

    cross_map: dict[int, list[int]] = {}

    for q in questions:
        t_slug = q.topic_dir

        # Get related topic slugs from map, or default to common foundation topics
        rel_slugs = RELATED_TOPICS_MAP.get(
            t_slug, ["core-devops-concepts", "cicd", "docker"]
        )

        # Find semantically related questions from target topics
        candidates = []
        for target_slug in rel_slugs:
            if target_slug not in topic_to_questions:
                continue

            target_questions = topic_to_questions[target_slug]

            # Score each target question by semantic similarity
            for tq in target_questions:
                if tq.id == q.id:
                    continue

                score = 0

                # Shared tags (highest weight)
                q_tags_set = set(tag.lower() for tag in q.tags)
                tq_tags_set = set(tag.lower() for tag in tq.tags)
                shared_tags = q_tags_set & tq_tags_set
                score += len(shared_tags) * 3

                # Same category
                if q.category.lower() == tq.category.lower():
                    score += 2

                # Shared terms in title/body (basic keyword matching)
                q_terms = set(q.title.lower().split()) | set(q.body.lower().split()[:100])
                tq_terms = set(tq.title.lower().split()) | set(tq.body.lower().split()[:100])
                # Filter out common stopwords
                stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'is', 'are', 'was', 'were', 'what', 'how', 'when', 'where', 'why', 'which', 'do', 'does'}
                q_terms = {t for t in q_terms if len(t) > 3 and t not in stopwords}
                tq_terms = {t for t in tq_terms if len(t) > 3 and t not in stopwords}
                shared_terms = q_terms & tq_terms
                score += min(len(shared_terms), 5)  # Cap term bonus

                if score > 0:
                    candidates.append((score, tq.id))

        # Sort by score (descending) and pick top 3
        candidates.sort(key=lambda x: x[0], reverse=True)
        cross_map[q.id] = [cand_id for score, cand_id in candidates[:3]]

    return cross_map


def main():
    topics = load_topics(REPO_ROOT)
    questions = all_questions(topics)

    # Validate question IDs before building any maps
    invalid_ids = []
    duplicate_ids = {}
    seen_ids = set()

    for q in questions:
        # Check for missing, non-numeric, or sentinel -1 IDs
        if q.id is None or q.id == -1:
            invalid_ids.append(f"{q.path}: ID is {q.id} (missing or sentinel)")
        elif not isinstance(q.id, int):
            invalid_ids.append(f"{q.path}: ID is non-integer: {q.id}")

        # Check for duplicate IDs
        if q.id in seen_ids:
            duplicate_ids.setdefault(q.id, []).append(q.path)
        else:
            seen_ids.add(q.id)

    # Fail loudly if validation errors found
    if invalid_ids or duplicate_ids:
        error_msg = "Question ID validation failed:\n"
        if invalid_ids:
            error_msg += "\nInvalid IDs:\n"
            for entry in invalid_ids:
                error_msg += f"  - {entry}\n"
        if duplicate_ids:
            error_msg += "\nDuplicate IDs:\n"
            for qid, paths in duplicate_ids.items():
                error_msg += f"  ID {qid} appears in:\n"
                for p in paths:
                    error_msg += f"    - {p}\n"
        raise SystemExit(error_msg)

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

        # Markers for generated content
        begin_marker = "<!-- BEGIN GENERATED RELATED TOPICS -->"
        end_marker = "<!-- END GENERATED RELATED TOPICS -->"

        # Build the generated section with markers
        # Blank lines around the markers keep the block Prettier-clean.
        generated_block = (
            f"{begin_marker}\n\n"
            f"## Related Concepts\n\n"
            + "\n".join(wikilink_items) + "\n\n"
            f"{end_marker}"
        )

        # Check if a marked block already exists (replace it)
        if begin_marker in content and end_marker in content:
            # Replace existing marked block
            pattern = re.compile(
                re.escape(begin_marker) + r".*?" + re.escape(end_marker),
                re.DOTALL
            )
            new_content = pattern.sub(generated_block, content)

        # Check for unmarked Related Concepts/Questions section (fail)
        elif "## Related Concepts" in content or "## Related Questions" in content:
            # Unmarked manual section - fail to avoid overwriting
            raise SystemExit(
                f"Error: {q.path} contains an unmarked '## Related Concepts' or '## Related Questions' section.\n"
                f"Please add markers {begin_marker} / {end_marker} or remove the section."
            )

        else:
            # No existing section - insert before footer
            footer_marker = "---"
            if footer_marker in content:
                parts = content.rsplit(footer_marker, 1)
                new_content = parts[0] + generated_block + "\n\n" + footer_marker + parts[1]
            else:
                new_content = content + "\n\n" + generated_block + "\n"

        q.path.write_text(new_content, encoding="utf-8")
        modified_count += 1
        
    print(f"Successfully processed {len(cross_link_map)} question mappings (injected into {modified_count} files).")


if __name__ == "__main__":
    main()
