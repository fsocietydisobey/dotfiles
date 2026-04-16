#!/bin/bash
# SessionStart hook — auto-injects architecture context into Claude Code at session start.
#
# Loads two files:
#   1. shared-docs/architecture/INDEX.md  — maps every domain to its architecture README
#   2. shared-docs/architecture/GLOSSARY.md — concept-to-file glossary for vague queries
#
# Why: the project has hand-curated architecture documentation that Claude should always
# be aware of. Without this hook, Claude has to remember to read it. With this hook, the
# context is injected at session start and Claude knows exactly where to look for any topic.
#
# The GLOSSARY in particular is the no-embeddings answer to "where's the rate limiting code?"
# style queries — Cursor solves this with vector embeddings; we solve it with hand-curated
# concept-to-file mappings that the user maintains.
#
# How: Claude Code reads stdout as JSON. The `hookSpecificOutput.additionalContext` field
# gets prepended to the model's context. Both files are concatenated into one block.
#
# Fails silently if files are missing (exit 0) — never block a session because a doc moved.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
INDEX_FILE="$PROJECT_DIR/shared-docs/architecture/INDEX.md"
GLOSSARY_FILE="$PROJECT_DIR/shared-docs/architecture/GLOSSARY.md"

# Bail if neither file exists — nothing to inject
if [ ! -f "$INDEX_FILE" ] && [ ! -f "$GLOSSARY_FILE" ]; then
  exit 0
fi

INDEX_FILE="$INDEX_FILE" GLOSSARY_FILE="$GLOSSARY_FILE" python3 <<'PYEOF'
import json
import os
import sys


def safe_read(path: str) -> str | None:
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path) as f:
            return f.read()
    except Exception:
        return None


index_content = safe_read(os.environ.get("INDEX_FILE", ""))
glossary_content = safe_read(os.environ.get("GLOSSARY_FILE", ""))

if not index_content and not glossary_content:
    sys.exit(0)

sections: list[str] = []

if index_content:
    sections.append(
        "# Architecture Map (auto-loaded at session start)\n\n"
        "This index maps every domain in the codebase to its architecture README. "
        "Read the relevant README before making changes to that layer. "
        "Always follow the conventions in .claude/rules/.\n\n"
        "---\n\n"
        + index_content
    )

if glossary_content:
    sections.append(
        "# Concept Glossary (auto-loaded at session start)\n\n"
        "This is the no-embeddings answer to vague queries. When the user asks about a "
        "topic without naming a file or symbol, check this glossary FIRST before grepping "
        "the codebase or using Serena. The user maintains this map by hand — trust it.\n\n"
        "---\n\n"
        + glossary_content
    )

output = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "\n\n===\n\n".join(sections),
    }
}

print(json.dumps(output))
PYEOF
