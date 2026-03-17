"""Semantic search for memory files using local embeddings."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from agentmem.chunker import chunk_text
from agentmem.config import AgentMemConfig

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    HAS_SEARCH = True
except ImportError:
    HAS_SEARCH = False


def _file_hash(path: Path) -> str:
    """Get hash of file contents for cache invalidation."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def _get_model(model_name: str) -> SentenceTransformer:
    """Load sentence transformer model (cached)."""
    if not HAS_SEARCH:
        raise ImportError(
            "Semantic search requires sentence-transformers. "
            "Install with: pip install agentmem[search]"
        )
    return SentenceTransformer(model_name)


def build_index(memory_dir: Path, config: AgentMemConfig | None = None) -> dict:
    """Build or update the semantic search index.

    Returns dict with stats: files_indexed, chunks_indexed, cached_files.
    """
    if config is None:
        config = AgentMemConfig()

    model = _get_model(config.embedding_model)
    cache_dir = memory_dir.parent / ".agentmem_cache"
    cache_dir.mkdir(exist_ok=True)

    index_file = cache_dir / "index.json"
    embeddings_file = cache_dir / "embeddings.json"

    # Load existing
    existing_index = json.loads(index_file.read_text()) if index_file.exists() else {}
    existing_embeddings = json.loads(embeddings_file.read_text()) if embeddings_file.exists() else {}

    # Find all .md files
    files_to_index: list[Path] = []
    for root, _dirs, filenames in os.walk(memory_dir):
        for fname in filenames:
            if fname.endswith(".md"):
                files_to_index.append(Path(root) / fname)

    new_index: dict = {}
    new_embeddings: dict = {}
    chunks_to_embed: list[str] = []
    chunk_keys: list[tuple[str, int]] = []
    cached_count = 0

    for file_path in files_to_index:
        rel_path = str(file_path.relative_to(memory_dir))
        current_hash = _file_hash(file_path)

        # Check if unchanged
        if rel_path in existing_index and existing_index[rel_path].get("hash") == current_hash:
            new_index[rel_path] = existing_index[rel_path]
            if rel_path in existing_embeddings:
                new_embeddings[rel_path] = existing_embeddings[rel_path]
            cached_count += 1
            continue

        # Read and chunk
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            continue

        chunks = chunk_text(text, config.chunk_size, config.chunk_overlap)

        new_index[rel_path] = {
            "hash": current_hash,
            "chunks": chunks,
        }

        for i, chunk in enumerate(chunks):
            chunks_to_embed.append(chunk["text"])
            chunk_keys.append((rel_path, i))

    # Embed new chunks
    if chunks_to_embed:
        embeddings = model.encode(chunks_to_embed, show_progress_bar=True)
        for (rel_path, chunk_idx), embedding in zip(chunk_keys, embeddings):
            if rel_path not in new_embeddings:
                new_embeddings[rel_path] = {}
            new_embeddings[rel_path][str(chunk_idx)] = embedding.tolist()

    # Save
    index_file.write_text(json.dumps(new_index, indent=2))
    embeddings_file.write_text(json.dumps(new_embeddings))

    total_chunks = sum(len(idx.get("chunks", [])) for idx in new_index.values())

    return {
        "files_indexed": len(new_index),
        "chunks_indexed": total_chunks,
        "cached_files": cached_count,
        "new_embeddings": len(chunks_to_embed),
    }


def search(
    memory_dir: Path,
    query: str,
    config: AgentMemConfig | None = None,
) -> list[dict]:
    """Search the index for relevant chunks.

    Returns list of dicts with keys: path, start_line, end_line, score, preview.
    """
    if config is None:
        config = AgentMemConfig()

    cache_dir = memory_dir.parent / ".agentmem_cache"
    index_file = cache_dir / "index.json"
    embeddings_file = cache_dir / "embeddings.json"

    if not index_file.exists() or not embeddings_file.exists():
        return []

    model = _get_model(config.embedding_model)
    index = json.loads(index_file.read_text())
    embeddings = json.loads(embeddings_file.read_text())

    # Embed query
    query_embedding = model.encode([query])[0]

    # Score all chunks
    results: list[dict] = []
    for rel_path, file_data in index.items():
        if rel_path not in embeddings:
            continue

        for chunk_idx, chunk in enumerate(file_data.get("chunks", [])):
            chunk_key = str(chunk_idx)
            if chunk_key not in embeddings[rel_path]:
                continue

            chunk_embedding = np.array(embeddings[rel_path][chunk_key])

            # Cosine similarity
            score = np.dot(query_embedding, chunk_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
            )

            if score >= config.search_min_score:
                results.append({
                    "path": rel_path,
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "score": float(score),
                    "preview": chunk["text"][:200] + "..."
                    if len(chunk["text"]) > 200
                    else chunk["text"],
                })

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[: config.search_top_k]
