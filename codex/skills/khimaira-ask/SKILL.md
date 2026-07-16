---
name: khimaira-ask
description: Ask another khimaira/Claude Code session a question and block until it answers, or a timeout fires. Use when you need a synchronous answer from a specific peer session in the same turn — not for FYI notes (use khimaira-tell) or leaving something for whoever opens next (use a project handoff).
metadata:
  short-description: Synchronous cross-session ask, blocks for the answer
---

# khimaira-ask

Wraps `mcp__khimaira__session_log_question` + `mcp__khimaira__session_wait_for_answer` so you
don't have to remember both steps. Ported from Claude Code's `/ask` slash command
(`~/.claude/commands/ask.md`) — same tools, same server (`khimaira`, not `khimaira-chat`).

## When to use

- "Does the spec at `<path>` say X or Y?" — the other session has context you don't.
- "Confirm before I proceed: was this done in commit Z or earlier?"
- Any question you need answered in THIS turn, not eventually.

For "FYI, no reply expected" send a notice instead (`mcp__khimaira__session_post_notice`). For "leave
this for whoever works here next" use a project handoff (`mcp__khimaira__session_post_handoff`).

## Steps

1. Resolve your own session id — Codex's SessionStart hook surfaces it as `khimaira session_id` in
   the boot context; fall back to `mcp__khimaira__session_list()` if you don't have it.
2. Call `mcp__khimaira__session_log_question(session_id=<your_id>, text=<question>,
   target_session_id=<target session id or name>)`. Capture the returned `question_id`.
3. Call `mcp__khimaira__session_wait_for_answer(session_id=<your_id>, question_id=<question_id>,
   timeout=<seconds, default 900>)`.
4. On answer: report the answer body verbatim, prefixed with which session answered.
5. On timeout: report that it timed out and the question is still open — it'll surface to the
   target on their next turn either way. Not an error, just unresolved this turn.

## Notes

- BLOCKING. The target session needs to actually run a turn (or be woken) for the answer to come
  back — a target that's sitting fully idle with no one prompting it will just time out.
- 900s default matches Claude Code's `/ask` — long enough to cover "target is mid-task and needs a
  moment," short enough not to hang forever.
- If you don't need the answer in THIS turn, call `session_log_question` alone (no wait) — it's the
  non-blocking version and doesn't need this skill.
