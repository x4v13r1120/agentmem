# Claude Code Integration

How to use agentmem with [Claude Code](https://docs.anthropic.com/claude/docs/claude-cli).

## Setup

1. Install agentmem in your project:

```bash
pip install agentmem[search]
agentmem init
```

2. Create `.claude.md` in your project root:

```markdown
# Memory System (agentmem)

## Before Answering Questions

When the user asks about:
- Past decisions or patterns
- "What did we learn about X?"
- "Have we tried this before?"
- Recurring errors or issues

**Required steps:**
1. Search memory: `agentmem search "query"`
2. Check graph connections: `cat memory/semantic/GRAPH_INDEX.md | grep -i "concept"`
3. Read specific files if needed: `cat memory/semantic/PATTERNS.md`

## Logging

### After significant events:
```bash
python -c "
from agentmem import log_outcome
from pathlib import Path
log_outcome(
    memory_dir=Path('./memory'),
    event_type='code',  # or 'api', 'system', 'integration', 'config'
    event='Brief description',
    outcome='success',  # or 'fail', 'surprise'
    details='What happened and why'
)
"
```

### When user corrects you:
Run correction detection immediately:
```bash
python -c "
from agentmem import detect_corrections, calculate_confidence
from agentmem.correction import save_correction, extract_rule
from pathlib import Path

message = '''[User's correction message]'''
corrections = detect_corrections(message)
if corrections:
    conf = calculate_confidence(corrections)
    if conf >= 0.70:
        primary = max(corrections, key=lambda c: 30 if c['category'] == 'explicit' else 15)
        rule = extract_rule(message, primary)
        save_correction(Path('./memory'), rule, primary['category'], conf)
        print(f'Correction saved: {rule}')
"
```

### Daily logs:
Append to `memory/episodic/YYYY-MM-DD.md`:
```bash
echo "## $(date +'%I:%M %p')\n[Your entry here]\n" >> memory/episodic/$(date +%Y-%m-%d).md
```

## Wiki-Links

When writing to memory files, use `[[wiki-links]]` for concepts:
```markdown
The [[API Timeout]] issue was resolved by increasing [[Request Timeout]] to 60s.
Connected to [[Error Handling]] patterns.
```

Rebuild graph after updates:
```bash
agentmem graph
```

## Tips

- Keep `memory/working/CURRENT.md` updated with active context
- Use `agentmem status` to check memory stats
- Search first, read targeted files second
- Log outcomes immediately after significant events
```

## Example Workflow

User: "Have we tried using Redis for caching before?"

```bash
# 1. Search memory
agentmem search "Redis caching"

# 2. Check graph for connections
cat memory/semantic/GRAPH_INDEX.md | grep -i "redis"

# 3. If found, read the specific file
cat memory/semantic/SYSTEMS.md | grep -A 10 "Redis"

# 4. Answer based on memory, or confirm no prior attempts
```

After implementing Redis caching:

```bash
# Log the outcome
python -c "
from agentmem import log_outcome
from pathlib import Path
log_outcome(
    memory_dir=Path('./memory'),
    event_type='system',
    event='Redis caching implementation',
    outcome='success',
    details='Implemented Redis for API response caching. Reduced average response time from 450ms to 80ms. Config in config/redis.yml.'
)
"

# Update current state
echo "## $(date +'%I:%M %p')\n**Redis Caching:** Implemented and tested. Monitoring performance.\n" >> memory/working/CURRENT.md

# Rebuild graph if you added [[wiki-links]]
agentmem graph
```
