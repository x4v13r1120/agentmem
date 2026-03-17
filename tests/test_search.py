"""Tests for semantic search.

Note: These tests require sentence-transformers to be installed.
They will be skipped if the package is not available.
"""

import pytest
from pathlib import Path
import tempfile

try:
    from agentmem.search import build_index, search
    from agentmem.config import AgentMemConfig

    HAS_SEARCH = True
except ImportError:
    HAS_SEARCH = False


@pytest.mark.skipif(not HAS_SEARCH, reason="sentence-transformers not installed")
def test_build_index():
    """Test index building."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir) / "memory"
        memory_dir.mkdir()

        # Create test files
        (memory_dir / "file1.md").write_text("The quick brown fox jumps over the lazy dog.")
        (memory_dir / "file2.md").write_text("Python is a programming language.")

        config = AgentMemConfig(memory_dir=str(memory_dir))
        stats = build_index(memory_dir, config)

        assert stats["files_indexed"] == 2
        assert stats["chunks_indexed"] >= 2
        assert stats["new_embeddings"] >= 2


@pytest.mark.skipif(not HAS_SEARCH, reason="sentence-transformers not installed")
def test_search_basic():
    """Test basic search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir) / "memory"
        memory_dir.mkdir()

        # Create test content
        (memory_dir / "programming.md").write_text(
            "Python is a high-level programming language known for its simplicity."
        )
        (memory_dir / "animals.md").write_text("Foxes are clever animals found in forests.")

        config = AgentMemConfig(memory_dir=str(memory_dir), search_min_score=0.0)
        build_index(memory_dir, config)

        # Search for programming
        results = search(memory_dir, "Python programming", config)
        assert len(results) > 0
        assert "programming.md" in results[0]["path"]

        # Search for animals
        results = search(memory_dir, "forest animals", config)
        assert len(results) > 0
        assert "animals.md" in results[0]["path"]


@pytest.mark.skipif(not HAS_SEARCH, reason="sentence-transformers not installed")
def test_cache_invalidation():
    """Test that index updates when files change."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir) / "memory"
        memory_dir.mkdir()

        file_path = memory_dir / "test.md"
        file_path.write_text("Original content")

        config = AgentMemConfig(memory_dir=str(memory_dir))
        stats1 = build_index(memory_dir, config)
        assert stats1["new_embeddings"] == 1

        # Rebuild without changes
        stats2 = build_index(memory_dir, config)
        assert stats2["new_embeddings"] == 0
        assert stats2["cached_files"] == 1

        # Modify file
        file_path.write_text("Modified content")
        stats3 = build_index(memory_dir, config)
        assert stats3["new_embeddings"] == 1
        assert stats3["cached_files"] == 0
