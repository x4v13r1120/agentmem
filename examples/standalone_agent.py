"""Example: Minimal AI agent using agentmem for persistent memory."""

from pathlib import Path
from datetime import datetime

# pip install agentmem[search]
from agentmem import (
    init_memory,
    search,
    rebuild_graph_index,
    detect_corrections,
    calculate_confidence,
    log_outcome,
)
from agentmem.config import AgentMemConfig
from agentmem.correction import save_correction


def setup_memory(memory_dir: Path) -> None:
    """Initialize memory if it doesn't exist."""
    if not memory_dir.exists():
        print(f"Initializing memory at {memory_dir}...")
        init_memory(memory_dir)
        print("✅ Memory initialized")


def recall(memory_dir: Path, query: str) -> list[dict]:
    """Search memory for relevant context."""
    print(f"🔍 Searching memory for: {query}")
    results = search(memory_dir, query, AgentMemConfig())
    for r in results[:3]:
        print(f"  [{r['score']:.2f}] {r['path']}:{r['start_line']}")
    return results


def log_to_episodic(memory_dir: Path, content: str) -> None:
    """Append to today's episodic log."""
    today = datetime.now().strftime("%Y-%m-%d")
    episodic_dir = memory_dir / "episodic"
    episodic_dir.mkdir(exist_ok=True)
    log_file = episodic_dir / f"{today}.md"

    if not log_file.exists():
        log_file.write_text(f"# {today}\n\n")

    timestamp = datetime.now().strftime("%I:%M %p")
    entry = f"## {timestamp}\n{content}\n\n"

    log_file.write_text(log_file.read_text() + entry)
    print(f"📝 Logged to {log_file.name}")


def process_user_message(memory_dir: Path, message: str) -> None:
    """Process a user message and handle corrections."""
    # Check for corrections
    corrections = detect_corrections(message)
    confidence = calculate_confidence(corrections)

    if corrections and confidence >= 0.70:
        print(f"⚠️  Correction detected (confidence: {confidence*100:.0f}%)")
        from agentmem.correction import extract_rule

        primary = max(corrections, key=lambda c: 30 if c["category"] == "explicit" else 15)
        rule = extract_rule(message, primary)
        save_correction(memory_dir, rule, primary["category"], confidence)
        print(f"✅ Saved correction: {rule}")


def main():
    """Run a simple agent with persistent memory."""
    memory_dir = Path("./agent_memory")
    setup_memory(memory_dir)

    # Example usage
    print("\n--- Agent Session Start ---\n")

    # Recall from memory
    recall(memory_dir, "previous decisions about API")

    # Log an event
    log_to_episodic(memory_dir, "User asked about API integration. Recommended REST.")

    # Log an outcome
    log_outcome(
        memory_dir=memory_dir,
        event_type="api",
        event="External API call",
        outcome="success",
        details="API responded in 200ms, returned expected data structure.",
    )

    # Simulate user correction
    user_message = "No, don't use REST. From now on, use GraphQL for new APIs."
    process_user_message(memory_dir, user_message)

    # Rebuild graph
    print("\n🔗 Rebuilding wiki-link graph...")
    rebuild_graph_index(memory_dir)
    print("✅ Graph updated")

    print("\n--- Session End ---")
    print(f"\nMemory persisted at: {memory_dir}")
    print("Run this script again to see memory recall in action!")


if __name__ == "__main__":
    main()
