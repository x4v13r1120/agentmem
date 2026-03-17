"""Command-line interface for agentmem."""

from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

from agentmem import __version__
from agentmem.config import AgentMemConfig, find_memory_dir
from agentmem.correction import calculate_confidence, detect_corrections
from agentmem.graph import rebuild_graph_index
from agentmem.init import init_memory


def _fix_encoding():
    """Fix Windows console encoding for emoji output."""
    if sys.platform == "win32":
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
        except Exception:
            pass


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize memory directory."""
    target = Path(args.path).resolve()
    if target.exists() and any(target.iterdir()):
        print(f"Error: {target} already exists and is not empty")
        return 1

    result = init_memory(target)
    print(f"[ok] Created memory structure at {target}")
    print(f"   Files created: {len(result['created_files'])}")
    if result["skipped_files"]:
        print(f"   Files skipped (already exist): {len(result['skipped_files'])}")

    print("\nNext steps:")
    print("  1. agentmem search 'your query' (requires: pip install agentmem[search])")
    print("  2. agentmem graph (build wiki-link graph)")
    print("  3. Add your first entry to working/CURRENT.md")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Search memory files."""
    try:
        from agentmem.search import build_index, search
    except ImportError:
        print("Error: Semantic search requires sentence-transformers")
        print("Install with: pip install agentmem[search]")
        return 1

    memory_dir = Path(args.path).resolve() if args.path else find_memory_dir()
    if not memory_dir.exists():
        print(f"Error: Memory directory not found: {memory_dir}")
        print("Run: agentmem init")
        return 1

    config = AgentMemConfig.find(memory_dir.parent)

    # Build/update index if needed
    if args.rebuild:
        print("Rebuilding search index...")
        stats = build_index(memory_dir, config)
        print(f"[ok] Indexed {stats['files_indexed']} files, {stats['chunks_indexed']} chunks")
        print(f"   Cached: {stats['cached_files']}, New embeddings: {stats['new_embeddings']}")
        if not args.query:
            return 0

    if not args.query:
        print("Error: query required (or use --rebuild to just rebuild index)")
        return 1

    results = search(memory_dir, args.query, config)

    if not results:
        print("No results found.")
        return 0

    print(f"\nTop {len(results)} results for: \"{args.query}\"\n")
    print("-" * 60)

    for i, r in enumerate(results, 1):
        print(f"\n{i}. [{r['score']:.3f}] {r['path']}:{r['start_line']}-{r['end_line']}")
        print(f"   {r['preview']}")

    return 0


def cmd_graph(args: argparse.Namespace) -> int:
    """Build wiki-link graph."""
    memory_dir = Path(args.path).resolve() if args.path else find_memory_dir()
    if not memory_dir.exists():
        print(f"Error: Memory directory not found: {memory_dir}")
        print("Run: agentmem init")
        return 1

    print("Building wiki-link graph...")
    output = rebuild_graph_index(memory_dir)
    print(f"[ok] Graph index written to {output.relative_to(memory_dir.parent)}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Show memory stats."""
    memory_dir = Path(args.path).resolve() if args.path else find_memory_dir()
    if not memory_dir.exists():
        print(f"Error: Memory directory not found: {memory_dir}")
        print("Run: agentmem init")
        return 1

    # Count files and size
    file_count = 0
    total_size = 0
    for filepath in memory_dir.rglob("*.md"):
        file_count += 1
        total_size += filepath.stat().st_size

    print(f"Memory Status: {memory_dir.name}/")
    print(f"   Files: {file_count} markdown files")
    print(f"   Size: {total_size / 1024:.1f} KB")

    # Episodic logs
    episodic_dir = memory_dir / "episodic"
    if episodic_dir.exists():
        episodic_count = len(list(episodic_dir.glob("*.md")))
        print(f"   Episodic logs: {episodic_count} days")

    # Semantic files
    semantic_dir = memory_dir / "semantic"
    if semantic_dir.exists():
        semantic_count = len(list(semantic_dir.glob("*.md")))
        print(f"   Semantic files: {semantic_count}")

    return 0


def cmd_detect(args: argparse.Namespace) -> int:
    """Detect corrections in a message (for testing)."""
    corrections = detect_corrections(args.message)
    confidence = calculate_confidence(corrections)

    if not corrections:
        print("No corrections detected")
        return 0

    print(f"Correction detected (confidence: {confidence*100:.0f}%)")
    print(f"   Patterns matched: {len(corrections)}")
    for c in corrections:
        print(f"   - {c['category']}: {c['match']}")

    if confidence < 0.70:
        print(f"\n   Confidence below threshold (70%), would not auto-save")
    else:
        print(f"\n   Confidence above threshold, would auto-save to PATTERNS.md")

    return 0


def main() -> int:
    """Main CLI entry point."""
    _fix_encoding()

    parser = argparse.ArgumentParser(
        prog="agentmem",
        description="Persistent memory system for AI agents",
    )
    parser.add_argument("--version", action="version", version=f"agentmem {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    init_parser = subparsers.add_parser("init", help="Initialize memory directory")
    init_parser.add_argument("--path", default="memory", help="Target directory (default: ./memory)")
    init_parser.set_defaults(func=cmd_init)

    # search
    search_parser = subparsers.add_parser("search", help="Search memory files")
    search_parser.add_argument("query", nargs="?", help="Search query")
    search_parser.add_argument("--path", help="Memory directory path")
    search_parser.add_argument("--rebuild", action="store_true", help="Rebuild search index first")
    search_parser.set_defaults(func=cmd_search)

    # graph
    graph_parser = subparsers.add_parser("graph", help="Build wiki-link graph")
    graph_parser.add_argument("--path", help="Memory directory path")
    graph_parser.set_defaults(func=cmd_graph)

    # status
    status_parser = subparsers.add_parser("status", help="Show memory stats")
    status_parser.add_argument("--path", help="Memory directory path")
    status_parser.set_defaults(func=cmd_status)

    # detect
    detect_parser = subparsers.add_parser("detect", help="Detect corrections in a message")
    detect_parser.add_argument("message", help="Message to analyze")
    detect_parser.set_defaults(func=cmd_detect)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
