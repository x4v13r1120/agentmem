# OpenClaw Integration

How to use agentmem with [OpenClaw](https://github.com/openclaw/openclaw) agents.

## Setup

1. Install agentmem in your OpenClaw workspace:

```bash
pip install agentmem[search]
cd ~/.openclaw/workspace
agentmem init
```

2. Update your `AGENTS.md`:

```markdown
## Memory Recall

Before answering questions about prior work, decisions, dates, people, preferences, or todos:
1. Run `memory_search` on MEMORY.md + memory/*.md
2. Check `memory/semantic/GRAPH_INDEX.md` for connected concepts from results
3. If graph shows connections to concepts NOT in search results, search those too
4. Pull specific lines with `memory_get` — don't read entire files

**Mandatory triggers:** External messages, new projects, recurring errors, architecture decisions, past corrections, preference questions.

**Rule:** If unsure whether to search, search.

## Auto-Save Triggers

**Always save:** User corrections, new people, credentials, API surprises, "save this"
**Rule:** When in doubt, save to episodic.

### Immediate Save-on-Correction

**Trigger words:** "no", "wrong", "stop", "don't", "do X instead", "that's not right", "I said", "actually"

**Action:** Before responding, IMMEDIATELY write the correction to today's episodic log:

```
## Correction — [time]
User said: [what they said]
I was doing: [what I was doing wrong]
Correct approach: [what to do instead]
```

**Why:** Corrections are the highest-value memory. They vanish after compaction if not saved instantly.
```

3. (Optional) Add a nightly cron to rebuild the graph:

```javascript
{
  "name": "rebuild-memory-graph",
  "schedule": { "kind": "cron", "expr": "0 4 * * *", "tz": "America/New_York" },
  "payload": {
    "kind": "agentTurn",
    "message": "Rebuild the memory graph index now. Run: exec command:'cd ~/.openclaw/workspace && agentmem graph' then report the result.",
    "timeoutSeconds": 120
  },
  "sessionTarget": "isolated"
}
```

## Usage in Agent Sessions

### Search memory

Use OpenClaw's built-in `memory_search` tool, which will search `MEMORY.md` and `memory/**/*.md` automatically.

### Manual graph check

```bash
exec command:"cat ~/.openclaw/workspace/memory/semantic/GRAPH_INDEX.md | grep -i 'concept name'"
```

### Log corrections manually

If auto-detection misses something:

```bash
exec command:"cd ~/.openclaw/workspace && python -c \"
from agentmem import detect_corrections, calculate_confidence
from agentmem.correction import save_correction, extract_rule
from pathlib import Path

message = '''User's correction message here'''
corrections = detect_corrections(message)
if corrections:
    confidence = calculate_confidence(corrections)
    if confidence >= 0.70:
        primary = max(corrections, key=lambda c: 30 if c['category'] == 'explicit' else 15)
        rule = extract_rule(message, primary)
        save_correction(Path('./memory'), rule, primary['category'], confidence)
        print(f'Saved: {rule}')
\""
```

## Tips

- Use `[[wiki-links]]` when writing to memory files
- Rebuild the graph weekly or after major updates
- Keep `working/CURRENT.md` up-to-date — it's your session state
- Log outcomes after significant events (API calls, deployments, bug fixes)
