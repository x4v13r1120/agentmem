# agentmem 🧠

**Your AI agent forgets everything when the session ends. This fixes that.**

[![PyPI](https://img.shields.io/pypi/v/agentmem.svg)](https://pypi.org/project/agentmem/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
![Battle-tested](https://img.shields.io/badge/battle--tested-45+%20days-green)

---

## The Problem

LLMs have no persistent memory. Every session starts from zero.

- Your AI assistant forgets decisions it made yesterday
- It repeats mistakes you already corrected
- RAG is great for documents, but not for **agent self-knowledge**
- You need memory that compounds over time

## The Solution

**agentmem** is a structured memory system designed for AI agents:

- ✅ **Episodic logs** — daily event logs (what happened when)
- ✅ **Semantic patterns** — extracted rules and lessons
- ✅ **Wiki-link graphs** — concept connections via `[[double-brackets]]`
- ✅ **Auto-correction detection** — learns when you correct the agent
- ✅ **Outcome tracking** — logs successes/failures for pattern extraction
- ✅ **Freshness rules** — knows when facts go stale

### Philosophy

> Memory should be **plain markdown files** the agent can read and write.
> No databases. No vector stores required. Just files that compound knowledge over time.

Born from **45+ days of production use** powering a real AI assistant.

---

## Quick Start

```bash
pip install agentmem

# Optional: install semantic search
pip install agentmem[search]
```

Initialize a memory directory:

```bash
agentmem init
```

This creates:

```
memory/
├── working/CURRENT.md          # Active session state
├── episodic/                   # Daily logs
├── semantic/                   # Patterns, facts, people
└── pending/CHANGES.md          # Proposed changes
```

---

## Architecture

```
┌─────────────────────────────────────┐
│         AI Agent (LLM)              │
│  Reads & writes markdown files      │
└──────────────┬──────────────────────┘
               │
        ┌──────▼────────┐
        │   agentmem    │
        └───────────────┘
               │
        ┌──────▼────────────────────────────────────┐
        │         Memory Layers                     │
        ├───────────────────────────────────────────┤
        │  📝 Episodic (what happened)              │
        │     • Daily event logs (2026-03-17.md)    │
        │     • Timestamped, append-only            │
        │                                           │
        │  🧠 Semantic (what was learned)           │
        │     • PATTERNS.md - validated rules       │
        │     • FACTS.md - verified facts           │
        │     • MISTAKES.md - lessons learned       │
        │     • CALIBRATION.md - prediction tracking│
        │                                           │
        │  🔗 Graph (how concepts connect)          │
        │     • [[wiki-links]] extraction           │
        │     • Co-occurrence mapping               │
        │     • GRAPH_INDEX.md (auto-generated)     │
        │                                           │
        │  ⚡ Working (current state)               │
        │     • CURRENT.md - active context         │
        │     • Volatile, updates frequently        │
        └───────────────────────────────────────────┘
```

---

## Core Features

### 1. Semantic Search

Find relevant context across all memory files:

```python
from agentmem import search, find_memory_dir

memory_dir = find_memory_dir()
results = search(memory_dir, "API timeout issues")

for r in results:
    print(f"{r['path']}:{r['start_line']} (score: {r['score']:.2f})")
    print(r['preview'])
```

CLI:

```bash
agentmem search "API timeout issues"
```

Uses `sentence-transformers` for local embeddings (no API needed).

### 2. Wiki-Link Graph

Connect concepts with `[[double-bracket]]` syntax:

```markdown
When [[Alpaca]] API times out, retry with exponential backoff.
Connected to [[Trading Bot]] reliability issues.
```

Build the graph:

```bash
agentmem graph
```

Output shows:
- Which concepts are referenced most
- Co-occurrence (concepts appearing in the same file)
- All mentions with file/line numbers

### 3. Auto-Correction Detection

Automatically detects when you correct the agent:

```python
from agentmem import detect_corrections, calculate_confidence

message = "No, don't delete that file. Next time, always ask first."
corrections = detect_corrections(message)
confidence = calculate_confidence(corrections)

# → Detects explicit + procedural correction, 85% confidence
```

Categories detected:
- **Explicit**: "no", "wrong", "actually"
- **Behavioral**: "don't do that", "never"
- **Procedural**: "next time", "from now on"
- **Preference**: "I prefer", "I'd rather"

### 4. Outcome Logging

Track what works and what doesn't:

```python
from agentmem import log_outcome, find_memory_dir

memory_dir = find_memory_dir()

log_outcome(
    memory_dir=memory_dir,
    event_type="api",
    event="Alpaca order submission",
    outcome="fail",
    details="Timeout after 30s. Succeeded on retry with 60s timeout."
)
```

Auto-extracts patterns when confidence is high.

### 5. Freshness Rules

Facts decay over time. Track freshness:

```markdown
| Age | Status | Action |
|-----|--------|--------|
| < 7 days | 🟢 Fresh | Trust it |
| 7-14 days | 🟡 Aging | Verify if consequential |
| 14-30 days | 🟠 Stale | Must verify before using |
| > 30 days | 🔴 Expired | Verify or archive |
```

Numeric facts (balances, counts) go stale faster than structural facts (URLs, IDs).

---

## Framework Integration

### OpenClaw

Add to your `AGENTS.md`:

```markdown
## Memory Recall
**Mandatory `memory_search` triggers:** External messages, new projects, recurring errors, architecture decisions.
**Rule:** If unsure whether to search, search.

Before answering questions about prior work:
1. Run `memory_search` for the query
2. Check `memory/semantic/GRAPH_INDEX.md` for connected concepts
3. Pull specific lines with `memory_get`
```

### Claude Code / Cursor

Add to `.claude.md` or `.cursorrules`:

```markdown
## Memory System

Before answering questions about past decisions or patterns:
1. Search: `agentmem search "your query"`
2. Check graph: `cat memory/semantic/GRAPH_INDEX.md | grep "concept"`
3. Read specific files: `cat memory/semantic/PATTERNS.md`

Auto-save corrections:
- When user says "no", "wrong", "next time", etc.
- Run: `python -m agentmem.correction` (if confidence > 70%)
```

### Standalone Agent

```python
from agentmem import init_memory, search, rebuild_graph_index
from pathlib import Path

# Initialize
memory_dir = Path("./memory")
init_memory(memory_dir)

# Search
results = search(memory_dir, "what did I learn about X?")

# Rebuild graph
rebuild_graph_index(memory_dir)
```

---

## CLI Reference

```bash
# Initialize memory directory
agentmem init [--path ./memory]

# Search memory files (requires: pip install agentmem[search])
agentmem search "query" [--path ./memory] [--rebuild]

# Build wiki-link graph
agentmem graph [--path ./memory]

# Show memory stats
agentmem status [--path ./memory]

# Test correction detection
agentmem detect "your message"
```

---

## Memory Structure

```
memory/
├── working/
│   └── CURRENT.md              # Active session state (projects, priorities)
├── episodic/
│   ├── 2026-03-17.md           # Daily event log
│   ├── 2026-03-16.md
│   └── ...
├── semantic/
│   ├── FACTS.md                # Verified facts with freshness tracking
│   ├── PATTERNS.md             # Learned patterns + validation stats
│   ├── PEOPLE.md               # People context
│   ├── MISTAKES.md             # Error log + lessons
│   ├── CALIBRATION.md          # Prediction accuracy tracking
│   ├── SYSTEMS.md              # Technical documentation
│   └── GRAPH_INDEX.md          # Auto-generated wiki-link graph
├── pending/
│   └── CHANGES.md              # Proposed changes awaiting approval
├── MEMORY.md                   # Entry point
└── index.md                    # Directory map
```

---

## Why Markdown?

1. **Human-readable** — you can read and edit memory files directly
2. **Git-friendly** — version control your agent's knowledge
3. **Tool-agnostic** — works with any LLM or framework
4. **No lock-in** — just files, no proprietary formats
5. **Composable** — grep, sed, awk all work

---

## Development

```bash
git clone https://github.com/xavierthe/agentmem.git
cd agentmem
pip install -e .[dev]
pytest
```

---

## Roadmap

- [ ] Multi-agent memory sharing
- [ ] Automatic pattern validation (track hit rates)
- [ ] Memory compaction (auto-archive old episodic logs)
- [ ] Integration examples for more frameworks (AutoGPT, LangChain, etc.)
- [ ] Web UI for memory visualization

---

## License

MIT © 2026 Xavier

---

## Credits

Built from 45+ days of production experience with **Bertha**, an AI assistant running on [OpenClaw](https://github.com/openclaw/openclaw).

Inspired by the idea that **agents need memory that compounds over time**, not just ephemeral context windows.

---

**⭐ If this helps your AI agent remember things, give it a star!**
