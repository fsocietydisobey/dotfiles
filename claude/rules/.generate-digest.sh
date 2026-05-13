#!/bin/bash
# Generate ~/.claude/rules/DIGEST.md from each rule's `## TL;DR` section.
#
# This file is AUTO-GENERATED. Don't edit DIGEST.md by hand — edit the
# `## TL;DR` section of the underlying rule file instead. Run this script
# (or let the pre-commit hook run it) to regenerate.
#
# Convention: every rule file in claude/rules/{personal,engineering}/*.md
# must start with a `# <Title>` line followed (eventually) by a `## TL;DR`
# section. The TL;DR is one to three sentences capturing the load-bearing
# principle of the rule — what the agent must remember when context is
# tight. The script extracts those sections and concatenates them.
#
# Exit non-zero (and lists offenders) if any rule file is missing TL;DR.
# That's the enforcement: a rule without a TL;DR fails the digest build,
# fails the pre-commit hook, fails CI.

set -euo pipefail

RULES_DIR="$(cd "$(dirname "$0")" && pwd)"
DIGEST="$RULES_DIR/DIGEST.md"

missing=()

{
  echo "# Rules Digest"
  echo ""
  echo "> **Auto-generated from each rule's \`## TL;DR\` section. Don't edit by hand —"
  echo "> edit the underlying rule and re-run \`claude/rules/.generate-digest.sh\`."
  echo "> Pre-commit hook regenerates on every commit that touches a rule.**"
  echo ""
  echo "_Load-bearing principles only. Full rule bodies live next to this file._"
  echo ""

  for category in personal engineering; do
    echo "## $category"
    echo ""
    for f in "$RULES_DIR/$category"/*.md; do
      [ -f "$f" ] || continue
      name=$(basename "$f" .md)
      # Extract `## TL;DR` section (until the next `## ` header)
      tldr=$(awk '/^## TL;DR$/{flag=1;next}/^## /{flag=0}flag' "$f" | sed '/^$/d')

      if [ -z "$tldr" ]; then
        missing+=("$category/$name.md")
        continue
      fi

      echo "**$name** — $tldr"
      echo ""
    done
  done

  echo "---"
  echo "_Regenerate: \`claude/rules/.generate-digest.sh\` · Source: each rule's TL;DR section_"
} > "$DIGEST"

if [ ${#missing[@]} -gt 0 ]; then
  echo "✗ ERROR: missing '## TL;DR' section in:" >&2
  for m in "${missing[@]}"; do echo "    $m" >&2; done
  echo "" >&2
  echo "Every rule file must start with '# <Title>' followed (eventually) by '## TL;DR'." >&2
  echo "See claude/rules/personal/workflow.md for the convention." >&2
  exit 1
fi

LINES=$(wc -l < "$DIGEST")
WORDS=$(wc -w < "$DIGEST")
echo "✓ DIGEST.md regenerated ($LINES lines, $WORDS words)"
