"""Wiki-link graph builder — extract [[links]] and build adjacency maps."""

from __future__ import annotations

import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


def extract_links(text: str) -> list[dict]:
    """Extract all [[wiki-links]] from text with line numbers.

    Returns list of dicts: raw, normalized, line, context.
    """
    links: list[dict] = []
    for i, line in enumerate(text.split("\n"), 1):
        for match in LINK_PATTERN.finditer(line):
            tag = match.group(1).strip()
            links.append({
                "raw": tag,
                "normalized": tag.lower().replace("  ", " "),
                "line": i,
                "context": line.strip()[:120],
            })
    return links


def extract_links_from_file(filepath: Path) -> list[dict]:
    """Extract wiki-links from a file."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
        return extract_links(text)
    except Exception:
        return []


def build_graph(memory_dir: Path) -> dict:
    """Build the full graph from all .md files in memory_dir.

    Returns dict with keys:
        tag_refs: tag -> list of {file, line, context, raw}
        file_tags: file -> list of tags
        tag_connections: tag -> set of co-occurring tags
    """
    tag_refs: dict[str, list[dict]] = defaultdict(list)
    file_tags: dict[str, list[str]] = defaultdict(list)
    tag_connections: dict[str, set[str]] = defaultdict(set)

    for root, _dirs, filenames in os.walk(memory_dir):
        for fname in filenames:
            if not fname.endswith(".md") or fname == "GRAPH_INDEX.md":
                continue

            filepath = Path(root) / fname
            relpath = str(filepath.relative_to(memory_dir))
            links = extract_links_from_file(filepath)

            tags_in_file: set[str] = set()
            for link in links:
                tag = link["normalized"]
                tag_refs[tag].append({
                    "file": relpath,
                    "line": link["line"],
                    "context": link["context"],
                    "raw": link["raw"],
                })
                file_tags[relpath].append(tag)
                tags_in_file.add(tag)

            # Co-occurrence: tags in same file are connected
            for tag in tags_in_file:
                tag_connections[tag].update(tags_in_file - {tag})

    return {
        "tag_refs": dict(tag_refs),
        "file_tags": dict(file_tags),
        "tag_connections": {k: v for k, v in tag_connections.items()},
    }


def generate_graph_index(memory_dir: Path) -> str:
    """Build graph and generate GRAPH_INDEX.md content."""
    graph = build_graph(memory_dir)
    tag_refs = graph["tag_refs"]
    file_tags = graph["file_tags"]
    tag_connections = graph["tag_connections"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# Memory Graph Index",
        f"*Auto-generated: {now}*",
        f"*Tags: {len(tag_refs)} | Files with links: {len(file_tags)}*",
        "",
        "## How to Use",
        "- Search this file for a concept to find all references + connected concepts",
        "- Connected tags = concepts that appear in the same file (likely related)",
        "- Use semantic search first, then check graph connections for related context",
        "",
        "---",
        "",
    ]

    # Sort by reference count
    sorted_tags = sorted(tag_refs.items(), key=lambda x: -len(x[1]))

    for tag, refs in sorted_tags:
        raw_forms = [r["raw"] for r in refs]
        display = max(set(raw_forms), key=raw_forms.count)

        lines.append(f"## [[{display}]]")
        lines.append(f"*{len(refs)} references*")
        lines.append("")

        connections = tag_connections.get(tag, set())
        if connections:
            sorted_conns = sorted(connections, key=lambda c: -len(tag_refs.get(c, [])))
            conn_display = ", ".join(f"[[{c}]]" for c in sorted_conns[:10])
            lines.append(f"**Connected:** {conn_display}")
            lines.append("")

        for ref in refs[:8]:
            lines.append(f"- `{ref['file']}#L{ref['line']}` — {ref['context'][:100]}")

        if len(refs) > 8:
            lines.append(f"- *...and {len(refs) - 8} more*")
        lines.append("")

    # File density summary
    lines.extend(["---", "", "## Files by Link Density", ""])
    sorted_files = sorted(file_tags.items(), key=lambda x: -len(x[1]))
    for filepath, tags in sorted_files[:20]:
        unique = len(set(tags))
        lines.append(f"- `{filepath}` — {unique} unique tags ({len(tags)} total)")

    return "\n".join(lines)


def rebuild_graph_index(memory_dir: Path) -> Path:
    """Rebuild GRAPH_INDEX.md and write it to disk."""
    content = generate_graph_index(memory_dir)
    output = memory_dir / "semantic" / "GRAPH_INDEX.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    return output
