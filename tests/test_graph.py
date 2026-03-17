"""Tests for wiki-link graph builder."""

from agentmem.graph import extract_links, build_graph
from pathlib import Path
import tempfile
import shutil


def test_extract_links():
    """Test wiki-link extraction."""
    text = """
    This mentions [[Alpaca]] and [[Trading Bot]].
    Also [[Alpaca]] again and [[New Concept]].
    """
    links = extract_links(text)
    assert len(links) == 4
    assert links[0]["raw"] == "Alpaca"
    assert links[0]["normalized"] == "alpaca"
    assert links[1]["raw"] == "Trading Bot"
    assert links[1]["normalized"] == "trading bot"


def test_extract_links_edge_cases():
    """Test edge cases in link extraction."""
    # Empty brackets
    assert extract_links("[[]]") == []

    # Whitespace
    text = "[[  Spaced  Out  ]]"
    links = extract_links(text)
    assert len(links) == 1
    assert links[0]["normalized"] == "spaced out"

    # Multiple on same line
    text = "[[First]] and [[Second]] here"
    links = extract_links(text)
    assert len(links) == 2


def test_build_graph():
    """Test full graph building."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)

        # Create test files
        (memory_dir / "file1.md").write_text("Mentions [[Concept A]] and [[Concept B]]")
        (memory_dir / "file2.md").write_text("Also [[Concept A]] and [[Concept C]]")
        (memory_dir / "file3.md").write_text("No links here")

        graph = build_graph(memory_dir)

        # Check tag_refs
        assert "concept a" in graph["tag_refs"]
        assert len(graph["tag_refs"]["concept a"]) == 2

        # Check file_tags
        assert "file1.md" in graph["file_tags"]

        # Check connections (co-occurrence)
        assert "concept b" in graph["tag_connections"]["concept a"]
        assert "concept c" in graph["tag_connections"]["concept a"]


def test_graph_ignores_graph_index():
    """Test that GRAPH_INDEX.md is ignored."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        (memory_dir / "GRAPH_INDEX.md").write_text("[[Should Ignore]]")
        (memory_dir / "other.md").write_text("[[Real Link]]")

        graph = build_graph(memory_dir)

        assert "should ignore" not in graph["tag_refs"]
        assert "real link" in graph["tag_refs"]
