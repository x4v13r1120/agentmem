"""Tests for correction detection."""

from agentmem.correction import detect_corrections, calculate_confidence, extract_rule


def test_explicit_corrections():
    """Test explicit correction patterns."""
    messages = [
        "No, that's wrong.",
        "Actually, you should do X instead.",
        "Nope, don't do that.",
        "I don't think so.",
    ]
    for msg in messages:
        corrections = detect_corrections(msg)
        assert len(corrections) > 0
        assert any(c["category"] == "explicit" for c in corrections)


def test_behavioral_corrections():
    """Test behavioral correction patterns."""
    messages = [
        "Don't do that again.",
        "Never delete files without asking.",
        "Stop sending so many messages.",
        "Always check first.",
    ]
    for msg in messages:
        corrections = detect_corrections(msg)
        assert len(corrections) > 0
        assert any(c["category"] == "behavioral" for c in corrections)


def test_procedural_corrections():
    """Test procedural correction patterns."""
    messages = [
        "Next time, verify before deploying.",
        "From now on, use X instead of Y.",
        "Going forward, check the docs.",
        "You should always test first.",
    ]
    for msg in messages:
        corrections = detect_corrections(msg)
        assert len(corrections) > 0
        assert any(c["category"] == "procedural" for c in corrections)


def test_preference_corrections():
    """Test preference correction patterns."""
    messages = [
        "I prefer the first option.",
        "I don't like when you do X.",
        "I'd rather you ask first.",
        "I want shorter responses.",
    ]
    for msg in messages:
        corrections = detect_corrections(msg)
        assert len(corrections) > 0
        assert any(c["category"] == "preference" for c in corrections)


def test_no_corrections():
    """Test messages with no corrections."""
    messages = [
        "That looks good!",
        "Thanks for the help.",
        "Can you explain how X works?",
    ]
    for msg in messages:
        corrections = detect_corrections(msg)
        assert len(corrections) == 0


def test_confidence_calculation():
    """Test confidence scoring."""
    # High confidence: explicit + multiple categories
    msg1 = "No, that's wrong. Next time, always verify first."
    corrections1 = detect_corrections(msg1)
    conf1 = calculate_confidence(corrections1)
    assert conf1 >= 0.70

    # Low confidence: single non-explicit
    msg2 = "Maybe try X next time?"
    corrections2 = detect_corrections(msg2)
    conf2 = calculate_confidence(corrections2)
    assert conf2 < 0.70

    # No corrections = 0
    assert calculate_confidence([]) == 0.0


def test_rule_extraction():
    """Test extracting rules from corrections."""
    msg = "No, don't delete that. Next time, always ask first."
    corrections = detect_corrections(msg)
    explicit = [c for c in corrections if c["category"] == "explicit"][0]
    rule = extract_rule(msg, explicit)
    assert "don't delete" in rule.lower() or "no" in rule.lower()
