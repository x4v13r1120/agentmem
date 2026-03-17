"""Initialize a new memory directory structure."""

from __future__ import annotations

from pathlib import Path

TEMPLATES = {
    "MEMORY.md": """\
# MEMORY.md — Memory System Entry Point

This file exists for compatibility with memory search tools.
The actual memory system lives in `memory/`.

**Quick Links:**
- [Memory Index](index.md) — Full map
- [Current State](working/CURRENT.md) — Active session state
- [Today's Log](episodic/) — Daily event logs

See `index.md` for the complete structure.
""",
    "index.md": """\
# Memory Index

*Map of the agent memory system.*

---

## Structure

```
memory/
├── working/
│   └── CURRENT.md          → Active session state (volatile)
├── episodic/
│   └── YYYY-MM-DD.md       → Daily event logs (append-only)
├── semantic/
│   ├── FACTS.md            → Verified facts with freshness rules
│   ├── PATTERNS.md         → Learned patterns + validation
│   ├── PEOPLE.md           → People context
│   ├── MISTAKES.md         → Error log + lessons learned
│   ├── CALIBRATION.md      → Prediction accuracy tracking
│   ├── SYSTEMS.md          → Technical documentation
│   └── GRAPH_INDEX.md      → Auto-generated wiki-link graph
└── pending/
    └── CHANGES.md          → Proposed changes awaiting approval
```

---

## Quick Reference

| I need... | Look in... |
|-----------|------------|
| What's happening now | working/CURRENT.md |
| What happened on a date | episodic/YYYY-MM-DD.md |
| Facts about systems | semantic/FACTS.md |
| Who is [person] | semantic/PEOPLE.md |
| Lessons learned | semantic/PATTERNS.md |
| How does [system] work | semantic/SYSTEMS.md |
| Pending changes | pending/CHANGES.md |

---

*Memory architecture: agentmem v0.1.0*
""",
    "working/CURRENT.md": """\
# CURRENT.md — Active Session State

*Volatile state. Update frequently during active work.*

---

## Active Projects

| Project | Status | Next Action |
|---------|--------|-------------|
| Example Project | 🟢 Active | Complete feature X |

---

## Open Positions

None currently.

---

## Priorities

1. **High:** [Task description]
2. **Medium:** [Task description]
3. **Low:** [Task description]

---

## Context

[Any active context the agent needs to remember for this session.]

---

*Last updated: [timestamp]*
""",
    "semantic/FACTS.md": """\
# FACTS.md — Verified Facts

*Things that are known to be true. Always cite source and date.*

---

## Freshness Rules

| Age | Status | Action |
|-----|--------|--------|
| < 7 days | 🟢 Fresh | Trust it |
| 7-14 days | 🟡 Aging | Verify if consequential |
| 14-30 days | 🟠 Stale | Must verify before using |
| > 30 days | 🔴 Expired | Move to Archive or verify |

**Numeric facts** (balances, counts) go stale faster — verify weekly.
**Structural facts** (URLs, IDs, credentials) stay fresh longer — verify monthly.

---

## System Facts

| Fact | Source | Date |
|------|--------|------|
| Example: Python 3.12 installed | system check | 2026-03-01 |
| Example: API key rotates monthly | docs | 2026-02-15 |

---

## User Context

| Fact | Source | Date |
|------|--------|------|
| Example: User prefers dark mode | conversation | 2026-03-10 |

---

*Last updated: [timestamp]*
""",
    "semantic/PATTERNS.md": """\
# PATTERNS.md — Learned Patterns & Rules

*Validated patterns extracted from experience. Include evidence and confidence.*

---

## Active Patterns

### Example Pattern — 2026-03-01
**Status:** ✅ VALIDATED (80% confidence, 12 trials)

**Evidence:**
- Occurred 10 times out of 12 attempts
- Consistent across different contexts

**Rule:**
When [trigger condition], expect [outcome]. Handle by [action].

**Validation:**
- First observed: 2026-02-15
- Last validated: 2026-03-01
- Hit rate: 10/12 (83%)

---

## Corrections

*Auto-detected when user corrects the agent*

### Example Correction — 2026-03-05
**Category:** Procedural
**Rule:** Next time, always verify before taking action.
**Confidence:** 85%

---

*Last updated: [timestamp]*
""",
    "semantic/PEOPLE.md": """\
# PEOPLE.md — People Context

*Information about people the agent interacts with.*

---

## People

### [Person Name]
- **Role:** [Their role/relationship]
- **Context:** [How they relate to the agent's work]
- **Preferences:** [Any known preferences]
- **Last interaction:** [Date]

**Notes:**
- [Relevant context about this person]

---

*Last updated: [timestamp]*
""",
    "semantic/MISTAKES.md": """\
# MISTAKES.md — Error Log & Lessons

*When things go wrong, log them here with what was learned.*

---

## Mistakes

### Example Mistake — 2026-03-01
**What happened:**
Deployed code without testing, broke production.

**Impact:**
High — service down for 30 minutes.

**Lesson:**
Always run test suite before deployment, even for "small" changes.

**Prevention:**
Added pre-deploy test gate to CI pipeline.

---

*Last updated: [timestamp]*
""",
    "semantic/CALIBRATION.md": """\
# CALIBRATION.md — Prediction Accuracy Tracking

*Track predictions with stated confidence to improve calibration.*

---

## How to Use
1. When making a prediction, log it here with confidence %
2. When outcome is known, mark as correct/incorrect
3. Review periodically to check if confidence matches reality

**Goal:** 70% confidence predictions should be correct ~70% of the time.

---

## Predictions

### Example Prediction — 2026-03-01
**Prediction:** Feature X will take 2 days to implement
**Confidence:** 70%
**Outcome:** ✅ Correct (took 2.5 days, within margin)
**Notes:** Underestimated testing time slightly

---

### Example Prediction — 2026-03-05
**Prediction:** User will prefer option A
**Confidence:** 85%
**Outcome:** ❌ Incorrect (user chose option B)
**Notes:** Overconfident — didn't consider context

---

## Calibration Stats

| Confidence Band | Predictions | Correct | Actual % |
|-----------------|-------------|---------|----------|
| 50-60% | 0 | 0 | - |
| 60-70% | 0 | 0 | - |
| 70-80% | 1 | 1 | 100% |
| 80-90% | 1 | 0 | 0% |
| 90-100% | 0 | 0 | - |

---

*Last updated: [timestamp]*
""",
    "semantic/SYSTEMS.md": """\
# SYSTEMS.md — Technical Documentation

*How things work. Document APIs, configs, architectures.*

---

## Systems

### Example System
**Type:** [API / Database / Service / etc.]
**Purpose:** [What it does]
**Location:** [URL / path / identifier]

**How it works:**
[Technical details]

**Known issues:**
- [Issue 1]
- [Issue 2]

**Last verified:** [Date]

---

*Last updated: [timestamp]*
""",
    "semantic/GRAPH_INDEX.md": """\
# Memory Graph Index

*Auto-generated by `agentmem graph`*

This file will be populated when you run:
```bash
agentmem graph
```

The graph extracts [[wiki-links]] from all memory files and shows:
- Which concepts are referenced most
- Which concepts co-occur (appear in the same file)
- Where each concept is mentioned

Use this to discover connections between ideas in your memory.
""",
    "pending/CHANGES.md": """\
# CHANGES.md — Pending Changes

*Proposed changes to memory structure or core patterns awaiting review.*

---

## Pending

[No pending changes]

---

*Last updated: [timestamp]*
""",
}


def init_memory(target_dir: Path) -> dict:
    """Initialize memory directory structure with templates.

    Returns dict with keys: created_files, skipped_files.
    """
    created: list[str] = []
    skipped: list[str] = []

    for rel_path, content in TEMPLATES.items():
        file_path = target_dir / rel_path
        if file_path.exists():
            skipped.append(rel_path)
            continue

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        created.append(rel_path)

    # Create episodic .gitkeep
    episodic_dir = target_dir / "episodic"
    episodic_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = episodic_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()
        created.append("episodic/.gitkeep")

    return {
        "created_files": created,
        "skipped_files": skipped,
    }
