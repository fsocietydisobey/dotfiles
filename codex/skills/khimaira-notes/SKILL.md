---
name: khimaira-notes
description: View another khimaira/Claude Code session's externalized state — recent decisions, open and answered questions, recent file touches, current status. Use for "what is session X up to / what did it decide about Y" — read-only, no side effects.
metadata:
  short-description: Read another session's decisions, questions, status
---

# khimaira-notes

Wraps `mcp__khimaira__session_state`, ported from Claude Code's `/notes` slash command
(`~/.claude/commands/notes.md`). Read-only — doesn't modify anything.

## When to use

- "What is session X up to right now?"
- "What did session X decide about Y?"
- Checking whether a peer session has an open question that targets you before you `khimaira-ask`
  it something it might already be waiting to tell you.

## Steps

1. Resolve the target — a session id or a friendly name (set via `session_set_name`). Required;
   there's no "no-args = my own session" shortcut — pass your own id explicitly if that's what you
   want.
2. Call `mcp__khimaira__session_state(session_id_or_name=<target>, recent=15)`.
3. Render compactly:
   - Status line: name (8-char id prefix) — status — last detail — updated `<relative time>`.
   - Recent decisions: timestamp + 1-line text, with `why` indented under if present.
   - Open questions: id + text + flag if `target_session_id` is you.
   - Answered questions (last 3-5): question + answer summary, truncated to ~200 chars.
   - Recent files touched: last 5-10 paths.
4. If an open question targets you specifically, surface it prominently at the end — that's
   actionable, not just informational.

## Notes

- For a chronological feed of decisions ACROSS all sessions (not just one), call
  `mcp__khimaira__session_recent_decisions()` directly instead.
- For substring search over a session's archived/drained inbox, use
  `mcp__khimaira__session_search_archive(...)`.
