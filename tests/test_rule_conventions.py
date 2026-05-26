"""Regression guards for ~/.claude/rules/personal/ discipline conventions."""

import os
from pathlib import Path

RULES_DIR = Path(os.path.expanduser("~/.claude/rules/personal"))


def test_bug_class_enumeration_has_evidence_quality_section():
    """Bug-class enumeration must distinguish audit-grade vs inspection-grade."""
    content = (RULES_DIR / "bug-class-enumeration.md").read_text()
    lowered = content.lower()
    assert "evidence quality" in lowered, "missing § Evidence quality"
    assert "audit-grade" in lowered, "missing audit-grade term"
    assert "inspection-grade" in lowered, "missing inspection-grade term"
    assert "UNKNOWN" in content, "missing UNKNOWN default reference"


def test_bug_class_enumeration_has_error_string_anti_pattern():
    """Bug-class enumeration must flag error-string-anchoring trap."""
    content = (RULES_DIR / "bug-class-enumeration.md").read_text()
    lowered = content.lower()
    assert "error-string anti-pattern" in lowered or "error string anti-pattern" in lowered, (
        "missing § Error-string anti-pattern"
    )
    assert "trap" in lowered or "anchor" in lowered, "missing anti-pattern framing"


def test_bug_class_enumeration_has_audit_first_threshold():
    """Bug-class enumeration must specify two-phase audit-first threshold."""
    content = (RULES_DIR / "bug-class-enumeration.md").read_text()
    lowered = content.lower()
    assert "audit-first threshold" in lowered, "missing § Audit-first threshold"
    assert "50%" in content or "two-phase" in lowered, "missing threshold metric"


def test_behavioral_rule_promotion_md_exists():
    """New rule file must exist + have TL;DR section + example gaps."""
    rule_file = RULES_DIR / "behavioral-rule-promotion.md"
    assert rule_file.exists(), f"missing rule file at {rule_file}"
    content = rule_file.read_text()
    assert "## TL;DR" in content, "missing TL;DR section (workflow.md convention)"
    assert "role-doc" in content.lower() and "themis" in content.lower() and "lint test" in content.lower(), (
        "missing 3-layer template enumeration"
    )
    examples = ("silent-sessions", "master-serializes", "master-defaults-to-user",
                 "worktree-stranding", "selector-scope", "idle-state")
    for ex in examples:
        assert ex in content.lower(), f"missing example gap: '{ex}'"
