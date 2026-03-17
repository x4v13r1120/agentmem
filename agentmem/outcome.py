"""Log outcomes for pattern extraction."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

OUTCOME_TYPES = {
    "api": "API Behavior",
    "code": "Code Execution",
    "system": "System Behavior",
    "integration": "Integration",
    "config": "Configuration",
}


def log_outcome(
    memory_dir: Path,
    event_type: str,
    event: str,
    outcome: str,
    details: str,
) -> dict:
    """Log an outcome to episodic memory and optionally extract a pattern.

    Args:
        memory_dir: Path to memory directory.
        event_type: One of: api, code, system, integration, config.
        event: Brief description of what happened.
        outcome: success, fail, or surprise.
        details: Detailed description.

    Returns:
        Dict with keys: success, actions, pattern (if extracted).
    """
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%I:%M %p")

    # Log to episodic
    episodic_dir = memory_dir / "episodic"
    episodic_dir.mkdir(parents=True, exist_ok=True)
    episodic_file = episodic_dir / f"{today}.md"

    if episodic_file.exists():
        content = episodic_file.read_text(encoding="utf-8")
    else:
        content = f"# {today}\n\n"

    emoji = "✅" if outcome == "success" else "❌" if outcome == "fail" else "⚠️"
    entry = f"## {emoji} {OUTCOME_TYPES.get(event_type, event_type)} Outcome ({timestamp})\n\n"
    entry += f"**Event:** {event}\n"
    entry += f"**Outcome:** {outcome.upper()}\n"
    entry += f"**Details:** {details}\n\n"

    content += entry
    episodic_file.write_text(content, encoding="utf-8")

    actions = ["logged_to_episodic"]

    # Try to extract pattern
    pattern = _extract_pattern(event_type, event, outcome, details)
    if pattern:
        _save_pattern(memory_dir, event_type, pattern)
        actions.append("extracted_pattern")

    result = {
        "success": True,
        "type": event_type,
        "event": event,
        "outcome": outcome,
        "actions": actions,
    }

    if pattern:
        result["pattern"] = pattern

    return result


def _extract_pattern(event_type: str, event: str, outcome: str, details: str) -> dict | None:
    """Try to extract a pattern from the outcome."""
    if outcome == "fail" and "timeout" in details.lower():
        return {
            "pattern": f"{OUTCOME_TYPES.get(event_type)} timeouts",
            "rule": f"When {event}, expect potential timeouts. Add retry logic or increase timeout.",
            "confidence": 0.75,
        }

    if outcome == "surprise" and "expected" in details.lower():
        return {
            "pattern": f"{OUTCOME_TYPES.get(event_type)} unexpected behavior",
            "rule": f"{event}: {details}",
            "confidence": 0.85,
        }

    if outcome == "success" and "after" in details.lower():
        return {
            "pattern": f"{OUTCOME_TYPES.get(event_type)} solution",
            "rule": f"For {event}: {details}",
            "confidence": 0.80,
        }

    return None


def _save_pattern(memory_dir: Path, event_type: str, pattern: dict) -> None:
    """Save pattern to PATTERNS.md or SYSTEMS.md."""
    target_file = (
        memory_dir / "semantic" / "SYSTEMS.md"
        if event_type == "api"
        else memory_dir / "semantic" / "PATTERNS.md"
    )

    if target_file.exists():
        content = target_file.read_text(encoding="utf-8")
    else:
        content = f"# {target_file.stem}.md\n\n"

    section_name = f"## {OUTCOME_TYPES.get(event_type, 'General')} Patterns"

    if section_name not in content:
        content += f"\n{section_name}\n\n"

    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"### {pattern['pattern']} — {today}\n"
    entry += f"**Rule:** {pattern['rule']}\n"
    entry += f"**Confidence:** {pattern['confidence']*100:.0f}%\n\n"

    section_start = content.find(section_name)
    next_section = content.find("\n## ", section_start + len(section_name))

    if next_section == -1:
        content += entry
    else:
        content = content[:next_section] + entry + content[next_section:]

    target_file.write_text(content, encoding="utf-8")
