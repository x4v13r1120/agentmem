"""Tests for text chunking."""

from agentmem.chunker import chunk_text


def test_basic_chunking():
    """Test basic chunking with no overlap."""
    text = "a" * 600
    chunks = chunk_text(text, chunk_size=300, overlap=0)
    assert len(chunks) == 2
    assert chunks[0]["start_line"] == 1
    assert chunks[1]["start_line"] == 1


def test_chunking_with_overlap():
    """Test chunking with overlap."""
    text = "\n".join([f"Line {i}" for i in range(1, 21)])
    chunks = chunk_text(text, chunk_size=100, overlap=30)
    assert len(chunks) >= 2
    # Check overlap exists
    first_chunk_lines = chunks[0]["text"].split("\n")
    second_chunk_lines = chunks[1]["text"].split("\n")
    assert any(line in second_chunk_lines for line in first_chunk_lines[-2:])


def test_empty_text():
    """Test chunking empty text."""
    assert chunk_text("") == []
    assert chunk_text("   \n  \n") == []


def test_single_short_chunk():
    """Test text shorter than chunk_size."""
    text = "Short text"
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    assert len(chunks) == 1
    assert chunks[0]["text"] == text
    assert chunks[0]["start_line"] == 1
    assert chunks[0]["end_line"] == 1


def test_line_numbers():
    """Test line number tracking."""
    text = "\n".join([f"Line {i}" for i in range(1, 11)])
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    assert chunks[0]["start_line"] == 1
    assert chunks[0]["end_line"] < 11
    assert chunks[-1]["end_line"] == 10


def test_exact_boundary():
    """Test chunking at exact boundary."""
    text = "a" * 500
    chunks = chunk_text(text, chunk_size=500, overlap=0)
    assert len(chunks) == 1
