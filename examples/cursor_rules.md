# Cursor Integration (.cursorrules)

Add this to your `.cursorrules` file to use agentmem with [Cursor](https://cursor.sh).

```markdown
## Memory System (agentmem)

This project uses agentmem for persistent memory across sessions.

### Before Answering Questions About:
- Past decisions, patterns, or lessons learned
- "Have we tried X before?"
- "What did we learn about Y?"
- Recurring errors or design choices

**Required:** Search memory first:
```bash
agentmem search "your query"
```

Check graph for related concepts:
```bash
cat memory/semantic/GRAPH_INDEX.md | grep -i "concept"
```

Read targeted files:
```bash
cat memory/semantic/PATTERNS.md
cat memory/semantic/MISTAKES.md
cat memory/semantic/SYSTEMS.md
```

### After Significant Events

Log outcomes immediately:
```python
from agentmem import log_outcome
from pathlib import Path

log_outcome(
    memory_dir=Path('./memory'),
    event_type='code',  # or 'api', 'system', 'integration', 'config'
    event='Brief description',
    outcome='success',  # or 'fail', 'surprise'
    details='What happened and why'
)
```

### When User Corrects You

**Trigger words:** "no", "wrong", "don't do that", "next time", "actually", "I said"

**Action:** Detect and save correction:
```python
from agentmem import detect_corrections, calculate_confidence
from agentmem.correction import save_correction, extract_rule
from pathlib import Path

message = "user's correction message"
corrections = detect_corrections(message)
if corrections:
    conf = calculate_confidence(corrections)
    if conf >= 0.70:
        primary = max(corrections, key=lambda c: 30 if c['category'] == 'explicit' else 15)
        rule = extract_rule(message, primary)
        save_correction(Path('./memory'), rule, primary['category'], conf)
```

### Writing to Memory

Use `[[wiki-links]]` for concepts:
```markdown
The [[Performance Issue]] was caused by [[N+1 Query]] pattern.
Fixed by implementing [[Eager Loading]].
```

Rebuild graph after updates:
```bash
agentmem graph
```

### Memory Structure

```
memory/
├── working/CURRENT.md          # Active session state
├── episodic/YYYY-MM-DD.md      # Daily event logs
├── semantic/
│   ├── PATTERNS.md             # Learned patterns
│   ├── MISTAKES.md             # Lessons from errors
│   ├── SYSTEMS.md              # Technical docs
│   └── GRAPH_INDEX.md          # Wiki-link graph
└── pending/CHANGES.md          # Proposed changes
```

### Rules

1. **Search before answering** — If unsure whether prior context exists, search
2. **Log corrections immediately** — Don't let them vanish
3. **Update CURRENT.md** — Keep active session state fresh
4. **Use wiki-links** — Help the graph find connections
5. **Rebuild graph weekly** — Or after major memory updates

### Commands

```bash
agentmem init              # Initialize memory directory
agentmem search "query"    # Search memory
agentmem graph             # Rebuild wiki-link graph
agentmem status            # Show memory stats
```
```

## Tips for Cursor

- Set a keybind for "Run Terminal Command" to quickly run `agentmem search`
- Use Cursor's "Chat with Codebase" alongside memory search for full context
- Keep `.cursorrules` and memory files in git for team knowledge sharing
