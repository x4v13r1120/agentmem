# Build Task: agentmem

You are building an open-source Python package called **agentmem** — a production-tested memory system for AI agents.

## Context
This is extracted from a real production system (an AI assistant running on OpenClaw). The memory system has been battle-tested for 45+ days with daily episodic logs, semantic pattern extraction, wiki-link graph indexing, correction detection, and outcome logging. We're open-sourcing the architecture and tooling, stripped of personal data.

## Package Structure

```
agentmem/
├── README.md
├── LICENSE                      # MIT
├── pyproject.toml               # Modern Python packaging (pip install agentmem)
├── .gitignore
├── agentmem/
│   ├── __init__.py              # Version, public API
│   ├── cli.py                   # CLI: agentmem init, search, graph, status
│   ├── init.py                  # Initialize memory directory structure
│   ├── search.py                # Semantic search (sentence-transformers)
│   ├── graph.py                 # Wiki-link graph builder
│   ├── correction.py            # Auto-detect user corrections
│   ├── outcome.py               # Log outcomes for pattern extraction
│   ├── chunker.py               # Text chunking with overlap
│   └── config.py                # Configuration management
│   └── templates/               # Template files for agentmem init
│       ├── MEMORY.md
│       ├── index.md
│       ├── working/
│       │   └── CURRENT.md
│       ├── episodic/
│       │   └── .gitkeep
│       ├── semantic/
│       │   ├── FACTS.md
│       │   ├── PATTERNS.md
│       │   ├── PEOPLE.md
│       │   ├── MISTAKES.md
│       │   ├── CALIBRATION.md
│       │   ├── SYSTEMS.md
│       │   └── GRAPH_INDEX.md
│       └── pending/
│           └── CHANGES.md
├── examples/
│   ├── openclaw_integration.md
│   ├── claude_code_integration.md
│   ├── cursor_rules.md
│   └── standalone_agent.py
└── tests/
    ├── test_search.py
    ├── test_graph.py
    ├── test_correction.py
    └── test_chunker.py
```

## README.md Requirements
1. **Hook:** "Your AI agent forgets everything when the session ends. This fixes that."
2. **The Problem:** LLMs have no persistent memory. Every session starts from zero. RAG is for documents, not agent self-knowledge.
3. **The Solution:** A structured memory system — episodic logs, semantic patterns, wiki-link graphs, correction detection, outcome tracking.
4. **Quick Start:** `pip install agentmem` then `agentmem init`
5. **ASCII architecture diagram** showing memory layers
6. **Key features** each with code examples:
   - Semantic search across memory files
   - Wiki-link graph for concept connections
   - Auto-correction detection
   - Outcome logging for pattern extraction
   - Freshness rules for facts
   - Framework integrations (OpenClaw, Claude Code, Cursor)
7. **Philosophy:** "Memory should be plain markdown files the agent can read and write. No databases. No vector stores required. Just files that compound knowledge over time."
8. **Battle-tested badge:** "Born from 45+ days of production use"

## Implementation Details

### search.py
- Use sentence-transformers (all-MiniLM-L6-v2) for local embeddings
- Chunk text with configurable overlap (default 500 chars, 100 overlap)
- Cosine similarity ranking
- Cache embeddings with file hash invalidation
- Index stored as JSON files alongside memory

### graph.py
- Extract [[wiki-links]] from all .md files
- Build adjacency map with co-occurrence (tags in same file are connected)
- Generate GRAPH_INDEX.md with: tag references, connected concepts, file density stats
- Sort by reference count

### correction.py
- Regex-based detection (no LLM needed, fast and free)
- Categories: explicit ("no", "wrong", "actually"), behavioral ("don't do that", "stop"), procedural ("next time", "from now on"), preference ("I prefer", "I'd rather")
- Confidence scoring based on pattern matches
- Auto-save to PATTERNS.md and episodic log when confidence > 70%

### outcome.py
- Log outcomes with type (api/code/system/integration/config)
- Track success/fail/surprise
- Auto-extract patterns from outcomes
- Save to episodic + semantic files

### cli.py
- `agentmem init [--path ./memory]` — Create memory directory with all templates
- `agentmem search "query" [--top 5]` — Semantic search
- `agentmem graph [--path ./memory]` — Rebuild wiki-link graph
- `agentmem status [--path ./memory]` — Stats: file count, size, staleness report

### Template Files
Include EXAMPLE entries (not real data) showing the format:
- FACTS.md: Freshness rules table + 3-4 example facts
- PATTERNS.md: 2 example patterns with status/evidence/rules
- PEOPLE.md: 2 example person entries
- MISTAKES.md: 2 example mistakes with lessons
- CALIBRATION.md: 2 example predictions with confidence tracking
- CURRENT.md: Example active state template

### Tests
Real pytest tests:
- test_chunker.py: Overlap correctness, edge cases (empty, single line, exact boundary)
- test_graph.py: Wiki-link extraction, adjacency building, co-occurrence
- test_correction.py: Each category detected correctly, confidence scoring, edge cases
- test_search.py: Index creation, query ranking, cache invalidation

## Key Design Principles
- Plain markdown, no database required
- Everything works offline, no API keys needed
- Correction detection uses regex, not LLM calls
- Wiki-links use [[double-bracket]] syntax
- Files are the source of truth — agents read and write them directly

Build ALL of this. Every file, fully implemented, production quality.
