#!/usr/bin/env python3
"""Generate an interactive HTML knowledge graph for GitHub Pages.

Parses all Markdown questions and topic indexes, extracts connections (categories,
shared tags, and explicit cross-file relative links), and builds an interactive 3D/2D
Force Graph using Force-Graph for GitHub Pages static site deployment.

Usage:
    python3 scripts/build_knowledge_graph.py [--output docs/index.html]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Add scripts dir to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib_content import REPO_ROOT, all_questions, load_topics, topic_meta

LINK_RE = re.compile(r"\[[^\]]*\]\((\.[^)\s]+)\)")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")

DIFFICULTY_COLORS = {
    "Beginner": "#10b981",      # Emerald Green
    "Intermediate": "#f59e0b",  # Amber Yellow
    "Advanced": "#ef4444",      # Rose Red
    "Topic": "#06b6d4",         # Cyan / Terminal Teal
}

GROUP_COLORS = {
    "Foundations": "#3b82f6",
    "Containers and Kubernetes": "#06b6d4",
    "Delivery and Automation": "#10b981",
    "Cloud Providers": "#8b5cf6",
    "Architecture and Scale": "#f59e0b",
    "Reliability and Operations": "#ec4899",
    "Security": "#ef4444",
    "Platform and Leadership": "#6366f1",
    "Interview Prep": "#14b8a6",
}


def extract_internal_links(file_path: Path, text: str, title_to_path_map: dict | None = None) -> list[Path]:
    """Extract relative markdown links and [[wikilinks]] targeting other question files."""
    linked_paths = []
    # 1. Standard relative markdown links
    for match in LINK_RE.findall(text):
        target = match.split("#", 1)[0]
        if not target or not target.endswith(".md"):
            continue
        resolved = (file_path.parent / target).resolve()
        if resolved.exists() and resolved != file_path:
            linked_paths.append(resolved)

    # 2. Obsidian / Wiki style [[wikilinks]]
    if title_to_path_map:
        for match in WIKILINK_RE.findall(text):
            target_name = match.strip().lower()
            if target_name in title_to_path_map:
                resolved = title_to_path_map[target_name]
                if resolved != file_path:
                    linked_paths.append(resolved)

    return linked_paths


def build_graph_data(repo_root: Path = REPO_ROOT) -> dict:
    topics = load_topics(repo_root)
    questions = all_questions(topics)
    meta = topic_meta()

    nodes = []
    edges = []
    edge_set = set()

    # 1. Add Topic Nodes
    for t in topics:
        t_group = meta.get(t.directory, {}).get("group", "Other")
        nodes.append({
            "id": f"topic:{t.directory}",
            "label": t.title,
            "group": "Topic Hub",
            "section": t_group,
            "val": 16,
            "color": GROUP_COLORS.get(t_group, DIFFICULTY_COLORS["Topic"]),
            "url": f"./{t.directory}/README.md",
            "category": t.title,
            "type": "topic"
        })

    # Path to Node ID map and Title to Path map
    path_to_id = {q.path.resolve(): f"q:{q.id}" for q in questions}
    title_to_path_map = {q.title.strip().lower(): q.path.resolve() for q in questions}
    for q in questions:
        title_to_path_map[f"q{q.id}"] = q.path.resolve()
        title_to_path_map[f"question {q.id}"] = q.path.resolve()
        title_to_path_map[f"#{q.id}"] = q.path.resolve()

    # 2. Add Question Nodes and Topic-to-Question Edges
    for q in questions:
        node_id = f"q:{q.id}"
        topic_dir = q.path.parent.name
        topic_node_id = f"topic:{topic_dir}"
        t_group = meta.get(topic_dir, {}).get("group", "Other")

        nodes.append({
            "id": node_id,
            "label": f"#{q.id} {q.title}",
            "title": q.title,
            "group": q.difficulty,
            "section": t_group,
            "val": 6 if q.difficulty == "Advanced" else (4 if q.difficulty == "Intermediate" else 3),
            "color": DIFFICULTY_COLORS.get(q.difficulty, "#3b82f6"),
            "url": f"./{q.path.relative_to(repo_root)}",
            "category": q.category,
            "difficulty": q.difficulty,
            "tags": q.tags,
            "type": "question"
        })

        # Connect Question to its Topic Node
        edge_key = (topic_node_id, node_id, "topic")
        if edge_key not in edge_set:
            edge_set.add(edge_key)
            edges.append({
                "source": topic_node_id,
                "target": node_id,
                "type": "topic-link",
                "color": "rgba(6, 182, 212, 0.4)"
            })

        # 3. Extract Explicit Markdown Links and [[wikilinks]] between Questions
        for linked_path in extract_internal_links(q.path, q.body, title_to_path_map):
            if linked_path in path_to_id:
                target_id = path_to_id[linked_path]
                e_key = (node_id, target_id, "cross-link")
                if e_key not in edge_set and (target_id, node_id, "cross-link") not in edge_set:
                    edge_set.add(e_key)
                    edges.append({
                        "source": node_id,
                        "target": target_id,
                        "type": "cross-link",
                        "color": "rgba(59, 130, 246, 0.6)"
                    })

    # 4. Connect Questions sharing identical specific tags (Tag Similarity Edges)
    tag_map: dict[str, list[str]] = {}
    for q in questions:
        for tag in q.tags:
            if tag in {"devops", "interview-questions"}:
                continue # Skip generic tags
            tag_map.setdefault(tag, []).append(f"q:{q.id}")

    for tag, q_ids in tag_map.items():
        if len(q_ids) > 1 and len(q_ids) <= 6:
            for i in range(len(q_ids)):
                for j in range(i + 1, len(q_ids)):
                    src, tgt = q_ids[i], q_ids[j]
                    e_key = (src, tgt, f"tag:{tag}")
                    if e_key not in edge_set and (tgt, src, f"tag:{tag}") not in edge_set:
                        edge_set.add(e_key)
                        edges.append({
                            "source": src,
                            "target": tgt,
                            "type": "tag-link",
                            "color": "rgba(245, 158, 11, 0.2)"
                        })

    return {"nodes": nodes, "links": edges}


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DevOps & Cloud Engineering Knowledge Graph</title>
  <script src="https://unpkg.com/3d-force-graph"></script>
  <script src="https://unpkg.com/three"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      padding: 0;
      background-color: #0b0f19;
      color: #e2e8f0;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      overflow: hidden;
    }}
    
    /* Header Panel */
    #header {{
      position: absolute;
      top: 20px;
      left: 20px;
      z-index: 20;
      background: rgba(15, 23, 42, 0.88);
      padding: 18px 22px;
      border-radius: 12px;
      border: 1px solid #1e293b;
      backdrop-filter: blur(12px);
      max-width: 380px;
      box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.6), 0 0 15px rgba(6, 182, 212, 0.15);
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 8px;
      border-radius: 6px;
      background: rgba(6, 182, 212, 0.12);
      color: #22d3ee;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
      border: 1px solid rgba(6, 182, 212, 0.3);
    }}
    .badge-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #22d3ee;
      box-shadow: 0 0 8px #22d3ee;
    }}
    h1 {{
      margin: 0 0 8px 0;
      font-size: 1.25rem;
      font-weight: 700;
      color: #f8fafc;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    p {{
      margin: 0 0 12px 0;
      font-size: 0.84rem;
      color: #94a3b8;
      line-height: 1.45;
    }}

    /* Search Bar */
    .search-box {{
      position: relative;
      margin-bottom: 12px;
    }}
    .search-box input {{
      width: 100%;
      padding: 8px 12px 8px 34px;
      background: rgba(30, 41, 59, 0.8);
      border: 1px solid #334155;
      border-radius: 8px;
      color: #f8fafc;
      font-family: 'Inter', sans-serif;
      font-size: 0.82rem;
      outline: none;
      transition: all 0.2s ease;
    }}
    .search-box input:focus {{
      border-color: #06b6d4;
      box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
    }}
    .search-icon {{
      position: absolute;
      left: 10px;
      top: 50%;
      transform: translateY(-50%);
      color: #64748b;
      font-size: 0.85rem;
    }}

    /* Legend */
    .legend {{
      display: flex;
      gap: 12px;
      font-size: 0.78rem;
      flex-wrap: wrap;
      padding-top: 8px;
      border-top: 1px solid rgba(51, 65, 85, 0.5);
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
      color: #cbd5e1;
    }}
    .dot {{
      width: 9px;
      height: 9px;
      border-radius: 50%;
      display: inline-block;
    }}

    /* Stats Bar */
    .stats-bar {{
      display: flex;
      justify-content: space-between;
      margin-top: 10px;
      padding-top: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      color: #64748b;
      border-top: 1px dashed rgba(51, 65, 85, 0.5);
    }}

    #graph {{
      width: 100vw;
      height: 100vh;
    }}

    /* Floating Inspector Card */
    #info-card {{
      position: absolute;
      bottom: 24px;
      right: 24px;
      z-index: 20;
      background: rgba(15, 23, 42, 0.92);
      padding: 18px 22px;
      border-radius: 14px;
      border: 1px solid #334155;
      display: none;
      width: 360px;
      box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.7), 0 0 20px rgba(6, 182, 212, 0.1);
      backdrop-filter: blur(12px);
      animation: slideUp 0.25s ease-out;
    }}
    @keyframes slideUp {{
      from {{ opacity: 0; transform: translateY(12px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .card-meta {{
      display: flex;
      gap: 6px;
      margin-bottom: 10px;
    }}
    .card-tag {{
      padding: 2px 8px;
      border-radius: 4px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
    }}
    #info-card h3 {{
      margin: 0 0 8px 0;
      font-size: 1.05rem;
      font-weight: 600;
      color: #f8fafc;
      line-height: 1.35;
    }}
    #info-card p {{
      margin: 0 0 14px 0;
      color: #cbd5e1;
      font-size: 0.82rem;
      line-height: 1.45;
    }}
    .card-actions {{
      display: flex;
      gap: 8px;
    }}
    #card-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #0284c7;
      color: #ffffff;
      padding: 8px 14px;
      border-radius: 8px;
      text-decoration: none;
      font-size: 0.8rem;
      font-weight: 600;
      transition: all 0.2s ease;
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }}
    #card-link:hover {{
      background: #0369a1;
      transform: translateY(-1px);
    }}
    .close-btn {{
      background: transparent;
      border: 1px solid #334155;
      color: #94a3b8;
      border-radius: 8px;
      padding: 8px 12px;
      cursor: pointer;
      font-size: 0.8rem;
    }}
    .close-btn:hover {{
      background: #1e293b;
      color: #f1f5f9;
    }}
  </style>
</head>
<body>
  <div id="header">
    <div class="badge"><span class="badge-dot"></span> Live Telemetry Topology</div>
    <h1>⚡ DevOps Knowledge Graph</h1>
    <p>Interactive 3D infrastructure map linking 500+ DevOps interview questions, platform topics, and architecture wikilinks.</p>
    
    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input type="text" id="search-input" placeholder="Filter questions or topics (e.g. docker, kubernetes)...">
    </div>

    <div class="legend">
      <div class="legend-item"><span class="dot" style="background:#06b6d4"></span> Topic Hub</div>
      <div class="legend-item"><span class="dot" style="background:#10b981"></span> Beginner</div>
      <div class="legend-item"><span class="dot" style="background:#f59e0b"></span> Intermediate</div>
      <div class="legend-item"><span class="dot" style="background:#ef4444"></span> Advanced</div>
    </div>

    <div class="stats-bar">
      <span>NODES: <strong id="node-count">0</strong></span>
      <span>EDGES: <strong id="edge-count">0</strong></span>
      <span>TOPICS: <strong>40</strong></span>
    </div>
  </div>

  <div id="info-card">
    <div class="card-meta">
      <span id="card-type" class="card-tag" style="background: rgba(6,182,212,0.2); color:#22d3ee">QUESTION</span>
      <span id="card-difficulty" class="card-tag" style="background: rgba(16,185,129,0.2); color:#34d399">BEGINNER</span>
    </div>
    <h3 id="card-title">Node Info</h3>
    <p id="card-desc"></p>
    <div class="card-actions">
      <a id="card-link" href="#" target="_blank">View Markdown Source ↗</a>
      <button class="close-btn" onclick="document.getElementById('info-card').style.display='none'">Dismiss</button>
    </div>
  </div>

  <div id="graph"></div>

  <script>
    const gData = {graph_json};

    document.getElementById('node-count').innerText = gData.nodes.length;
    document.getElementById('edge-count').innerText = gData.links.length;

    const card = document.getElementById('info-card');
    const cardType = document.getElementById('card-type');
    const cardDifficulty = document.getElementById('card-difficulty');
    const cardTitle = document.getElementById('card-title');
    const cardDesc = document.getElementById('card-desc');
    const cardLink = document.getElementById('card-link');

    const Graph = ForceGraph3D()
      (document.getElementById('graph'))
        .graphData(gData)
        .nodeId('id')
        .nodeVal('val')
        .nodeColor('color')
        .nodeLabel('label')
        .nodeResolution(16)
        .linkOpacity(0.35)
        .linkWidth(link => link.type === 'topic-link' ? 1.8 : 0.8)
        .linkColor(link => link.color || 'rgba(148, 163, 184, 0.25)')
        .linkDirectionalParticles(link => link.type === 'cross-link' ? 3 : 0)
        .linkDirectionalParticleWidth(2.0)
        .linkDirectionalParticleSpeed(0.006)
        .onNodeHover(node => {{
          document.body.style.cursor = node ? 'pointer' : 'default';
        }})
        .onNodeClick(node => {{
          if (node) {{
            const distance = 120;
            const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
            Graph.cameraPosition(
              {{ x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }},
              node,
              2000
            );

            if (node.type === 'topic') {{
              cardType.innerText = 'TOPIC HUB';
              cardType.style.background = 'rgba(6, 182, 212, 0.25)';
              cardType.style.color = '#22d3ee';
              cardDifficulty.innerText = node.section || 'DOMAIN';
              cardDifficulty.style.background = 'rgba(139, 92, 246, 0.25)';
              cardDifficulty.style.color = '#c084fc';
            }} else {{
              cardType.innerText = 'QUESTION';
              cardType.style.background = 'rgba(59, 130, 246, 0.25)';
              cardType.style.color = '#60a5fa';
              cardDifficulty.innerText = (node.difficulty || 'GENERAL').toUpperCase();
              
              const diffColors = {{
                'Beginner': {{ bg: 'rgba(16,185,129,0.25)', fg: '#34d399' }},
                'Intermediate': {{ bg: 'rgba(245,158,11,0.25)', fg: '#fbbf24' }},
                'Advanced': {{ bg: 'rgba(239,68,68,0.25)', fg: '#f87171' }}
              }};
              const colors = diffColors[node.difficulty] || {{ bg: 'rgba(148,163,184,0.25)', fg: '#cbd5e1' }};
              cardDifficulty.style.background = colors.bg;
              cardDifficulty.style.color = colors.fg;
            }}

            cardTitle.innerText = node.label;
            cardDesc.innerText = `Domain: ${{node.section || node.category || 'DevOps Platform'}}\\nCategory: ${{node.category || 'Topic Index'}}\\nNode Type: ${{node.type}}`;
            cardLink.href = `https://github.com/mchittineni/ultimate-devops-guide/blob/main/${{node.url.replace('./', '')}}`;
            card.style.display = 'block';
          }}
        }});

    // Live search filter
    document.getElementById('search-input').addEventListener('input', (e) => {{
      const query = e.target.value.strip ? e.target.value.strip().toLowerCase() : e.target.value.toLowerCase().trim();
      if (!query) {{
        Graph.nodeColor(node => node.color);
        return;
      }}
      Graph.nodeColor(node => {{
        const label = (node.label || '').toLowerCase();
        const cat = (node.category || '').toLowerCase();
        const sec = (node.section || '').toLowerCase();
        if (label.includes(query) || cat.includes(query) || sec.includes(query)) {{
          return '#38bdf8'; // Highlight cyan
        }}
        return 'rgba(51, 65, 85, 0.25)'; // Dim unmatched
      }});
    }});

    // Physics Tuning
    Graph.d3Force('charge').strength(-130);
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "-o", default="docs/index.html", help="Target output HTML file path")
    args = parser.parse_args()

    graph_data = build_graph_data()

    output_path = REPO_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html_content = HTML_TEMPLATE.format(graph_json=json.dumps(graph_data, indent=2))
    output_path.write_text(html_content, encoding="utf-8")

    print(f"Successfully generated DevOps Knowledge Graph UI at: {output_path}")
    print(f"Nodes: {len(graph_data['nodes'])}, Edges: {len(graph_data['links'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
