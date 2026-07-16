---
name: khimaira-tell
description: Send a one-way FYI to another khimaira/Claude Code session OR to a khimaira-attached project (any future session working there will see it). Use for "no reply needed" notes — not for questions you need answered this turn (use khimaira-ask).
metadata:
  short-description: One-way send, smart-routed to a session or a project
---

# khimaira-tell

Smart-routed one-way send, ported from Claude Code's `/tell` slash command
(`~/.claude/commands/tell.md`). The target can be a session name (delivered as a notice to that
session's inbox) or a khimaira-attached project label like `backend`/`khimaira` (delivered as a
project handoff scoped to that project's cwd — any future session there sees it). You don't pick
which; the server figures it out.

## When to use

- "FYI session X, I went with option C" — no reply needed.
- "FYI anyone working in jeevy_portal, starting from commit Y watch for Z."
- Any note where the receiver doesn't need to respond in real time.

For a synchronous answer in THIS turn, use `khimaira-ask` instead.

## Steps

1. Resolve your own session id (sender) — from the SessionStart hook boot context, or
   `mcp__khimaira__session_list()` as fallback.
2. Hit the smart-route endpoint:
   ```bash
   curl -sS -X POST 'http://127.0.0.1:8740/api/route' \
     -H 'Content-Type: application/json' \
     -d '{"target":"<target>","text":"<message>","from_session_id":"<your_id>"}'
   ```
3. Read `routed_as` in the response:
   - `"notice"` — delivered to a session's inbox; surfaces on their next turn.
   - `"project_handoff"` — scoped to a project's cwd; surfaces on any future session's
     SessionStart there (7-day TTL by default).
4. On 404 (neither a session nor a project matched): report the response detail verbatim and
   suggest checking `khimaira attached` (project labels) or `session_list()` (session names).

## Notes

- Don't ask the user to disambiguate a session name vs. a project label with the same string — let
  the server route it.
- Notices auto-expire after being surfaced 3 times if never explicitly acknowledged.
