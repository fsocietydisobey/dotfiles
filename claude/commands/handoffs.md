# /handoffs — Pull pending khimaira handoffs into this session

Surface any cwd-scoped khimaira handoffs that have been posted to this
project. Two-mode behavior depending on what's pending:

1. **New handoffs since boot** → consume them (mark read, auto-claim
   ownership), render the directive framing. Same effect as
   SessionStart's auto-surface.
2. **Nothing new, but this session has previously-consumed handoffs**
   → re-surface them in a read-only "previously consumed" view so the
   user can re-read what was already delivered. This addresses the
   common case where the user invokes `/handoffs` MANUALLY because
   they want to see the content again (the SessionStart hook
   consumed it on boot, marked-read; without this fallback the
   command unhelpfully reports "📭 nothing new" with no content).
3. **Nothing pending and nothing previously consumed** → truly empty.

## Steps

1. Resolve this session's id (from SessionStart hook context, or
   `mcp__khimaira__session_list()` fallback).
2. Resolve `cwd` (`$CLAUDE_PROJECT_DIR` or the parent dir of files
   you've been editing).
3. Call `mcp__khimaira__session_consume_handoffs(session_id, cwd)` to
   get any NEW handoffs and mark them read.
4. **If the consume returned non-empty**, render per the
   "Render — new handoffs" section below and STOP. Standard handoff
   directive framing applies; treat as task list, propose first
   action, start.
5. **If consume returned EMPTY**, fall back to a peek via
   `curl -sS 'http://127.0.0.1:8740/api/handoffs/in-scope?session_id=<id>&cwd=<cwd>'`
   (or directly via the daemon's
   `mcp__khimaira__session_state(<session_id>)` if that exposes the
   per-session read_by list — depends on which is cheaper to read).
   Filter to handoffs where `session_id ∈ read_by` AND `expires_at >
   now`. Sort by `ts` descending. Take the most recent ~5.
6. Render per the "Render — previously consumed" section. NOT
   directives anymore (the agent already consumed them); read-only
   reference view for the user.

## Render — new handoffs (consume returned non-empty)

For OWNED handoffs:

```
📦 khimaira handoffs — N directive(s) you now OWN in <cwd>:

- [handoff abc12345 · 2026-05-12T14:30:00 · from def67890]
  <handoff text>

Treat these as directives, not FYIs. Read referenced files, pick the
highest-priority item, propose a first action, and START.
```

For handoffs another session already claimed:

```
👀 khimaira handoffs — N already-claimed handoff(s) in <cwd>:
- [handoff abc12345 · from def67890 · OWNED BY 9d45c212]
  <handoff text>
```

## Render — previously consumed (consume empty, fallback view)

```
📭 No new handoffs since boot in <cwd>.

📥 Previously consumed by this session (read-only, most recent N):

- [handoff abc12345 · 2026-05-13T14:30:00 · from def67890 · consumed at SessionStart]
  <handoff text — full body, NOT just the first line>

These were already surfaced when you booted; showing them again here
because you ran `/handoffs` manually. To act on one, treat its
content as still-active and propose a concrete first action. To peek
at others' handoffs (not consumed by you), call
`session_state(<sender>)` directly.
```

## Render — truly empty

```
📭 No handoffs in scope <cwd> for session <id> — nothing pending,
nothing previously consumed.
```

## When NOT to use

- For "messages targeted at me by name" — use `/inbox` instead.
  Handoffs are cwd-scoped; inbox notes are session-targeted.

## Notes

- Step 5's peek does NOT mark anything read — handoffs you've already
  consumed stay consumed. The "previously consumed" view is purely
  for re-reading.
- Don't invent UI for the user. If the user just wants to re-read the
  handoff that came in at boot, the "previously consumed" view IS the
  answer. Don't tell them to grep boot-output files.
- Always include the full handoff text body in the rendered output,
  not just the first line or a summary — the user invoked
  `/handoffs` because they wanted to SEE the content.
