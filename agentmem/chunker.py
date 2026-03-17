"""Text chunking with configurable overlap for semantic search."""

from __future__ import annotations


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[dict]:
    """Split text into overlapping chunks with line number tracking.

    Args:
        text: Input text to chunk.
        chunk_size: Maximum characters per chunk.
        overlap: Character overlap between consecutive chunks.

    Returns:
        List of dicts with keys: text, start_line, end_line.
    """
    if not text or not text.strip():
        return []

    lines = text.split("\n")
    chunks: list[dict] = []
    current_lines: list[str] = []
    current_size = 0
    start_line = 1

    for i, line in enumerate(lines, 1):
        line_len = len(line) + 1  # +1 for newline

        if current_size + line_len > chunk_size and current_lines:
            # Emit current chunk
            chunks.append({
                "text": "\n".join(current_lines),
                "start_line": start_line,
                "end_line": i - 1,
            })

            # Keep overlap lines
            overlap_lines: list[str] = []
            overlap_size = 0
            for prev_line in reversed(current_lines):
                if overlap_size + len(prev_line) + 1 > overlap:
                    break
                overlap_lines.insert(0, prev_line)
                overlap_size += len(prev_line) + 1

            current_lines = overlap_lines
            current_size = overlap_size
            start_line = i - len(overlap_lines)

        current_lines.append(line)
        current_size += line_len

    # Final chunk
    if current_lines:
        chunks.append({
            "text": "\n".join(current_lines),
            "start_line": start_line,
            "end_line": len(lines),
        })

    return chunks
