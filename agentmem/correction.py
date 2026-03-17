"""Auto-detect when a user corrects the agent."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

# Correction pattern matchers
PATTERNS = {
    "explicit": [
        r"\b(no|nah|nope),?\s",
        r"\b(wrong|incorrect|not right)\b",
        r"\bactually\b",
        r"\bthat'?s\s+(not|wrong|incorrect)",
        r"\bdon'?t\s+think\s+so\b",
    ],
    "behavioral": [
        r"\b(don'?t|never|stop)\s+(do|doing)\s+that\b",
        r"\bnever\s+\w+",
        r"\balways\s+\w+",
        r"\bstop\s+\w+ing",
        r"\bquit\s+\w+ing",
    ],
    "procedural": [
        r"\b(next time|from now on|going forward)\b",
        r"\binstead\s+of\s+\w+,?\s+\w+",
        r"\byou should\s+(have\s+)?",
        r"\bmake sure\s+(you|to)\s+",
    ],
    "preference": [
        r"\bI\s+(prefer|like|want)\b",
        r"\bI\s+don'?t\s+(like|want)\b",
        r"\bI'?d\s+rather\b",
    ],
}


def detect_corrections(message: str) -> list[dict]:
    """Detect correction patterns in a message.

    Returns list of dicts with keys: category, pattern, match, context, position.
    """
    corrections: list[dict] = []

    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, message, re.IGNORECASE):
                start = max(0, match.start() - 50)
                end = min(len(message), match.end() + 100)
                context = message[start:end].strip()

                corrections.append({
                    "category": category,
                    "pattern": pattern,
                    "match": match.group(),
                    "context": context,
                    "position": match.start(),
                })

    return corrections


def calculate_confidence(corrections: list[dict]) -> float:
    """Calculate confidence that this is actually a correction.

    Explicit corrections are highest confidence. Multiple categories increase confidence.
    """
    if not corrections:
        return 0.0

    categories_hit = len(set(c["category"] for c in corrections))
    explicit_count = sum(1 for c in corrections if c["category"] == "explicit")
    other_count = len(corrections) - explicit_count

    confidence = 0.0
    confidence += explicit_count * 0.30
    confidence += other_count * 0.15
    confidence += categories_hit * 0.10

    return min(confidence, 1.0)


def extract_rule(message: str, correction: dict) -> str:
    """Extract the actionable rule from the correction."""
    category = correction["category"]

    if category == "explicit":
        sentences = re.split(r"[.!?]\s+", message)
        for sent in sentences:
            if correction["match"].lower() in sent.lower():
                return sent.strip()

    elif category == "behavioral":
        match = re.search(
            r"(don'?t|never|stop|always)\s+(\w+(?:\s+\w+){0,5})",
            message,
            re.IGNORECASE,
        )
        if match:
            return f"{match.group(1).capitalize()} {match.group(2)}"

    elif category == "procedural":
        match = re.search(
            r"(next time|from now on|going forward)[,:]?\s+(.+?)(?:[.!?]|$)",
            message,
            re.IGNORECASE,
        )
        if match:
            return f"{match.group(1).capitalize()}: {match.group(2).strip()}"

    elif category == "preference":
        match = re.search(
            r"I\s+(prefer|like|want|don'?t\s+like|don'?t\s+want|'?d\s+rather)\s+(.+?)(?:[.!?]|$)",
            message,
            re.IGNORECASE,
        )
        if match:
            return f"User {match.group(1)}: {match.group(2).strip()}"

    return correction["context"]


def save_correction(
    memory_dir: Path,
    rule: str,
    category: str,
    confidence: float,
) -> None:
    """Save correction to PATTERNS.md and episodic log."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Save to PATTERNS.md
    patterns_file = memory_dir / "semantic" / "PATTERNS.md"
    if patterns_file.exists():
        content = patterns_file.read_text(encoding="utf-8")
    else:
        content = "# PATTERNS.md\n\n"

    if "## Corrections" not in content:
        content += "\n## Corrections\n\n*Auto-detected when user corrects the agent*\n\n"

    entry = f"### {category.capitalize()} — {today}\n"
    entry += f"**Rule:** {rule}\n"
    entry += f"**Confidence:** {confidence*100:.0f}%\n\n"

    match = re.search(r"(## Corrections.*?)(## \w+|\Z)", content, re.DOTALL)
    if match:
        insert_pos = match.end(1)
        content = content[:insert_pos] + entry + content[insert_pos:]
    else:
        content += entry

    patterns_file.write_text(content, encoding="utf-8")

    # Save to episodic log
    episodic_dir = memory_dir / "episodic"
    episodic_dir.mkdir(parents=True, exist_ok=True)
    episodic_file = episodic_dir / f"{today}.md"

    if episodic_file.exists():
        episodic_content = episodic_file.read_text(encoding="utf-8")
    else:
        episodic_content = f"# {today}\n\n"

    timestamp = datetime.now().strftime("%I:%M %p")
    episodic_entry = f"## Correction Detected ({timestamp})\n\n"
    episodic_entry += f"**Category:** {category.capitalize()}\n"
    episodic_entry += f"**Rule:** {rule}\n\n"

    episodic_content += episodic_entry
    episodic_file.write_text(episodic_content, encoding="utf-8")
