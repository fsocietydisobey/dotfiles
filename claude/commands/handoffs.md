# /handoffs — Pull pending chimera handoffs into this session

Surface any cwd-scoped chimera handoffs that have been posted to this
project since this session started. SessionStart's auto-surfacing only
fires once at boot — when someone posts a handoff to your project
after you've opened Claude Code, it can't reach you without this.

## What it does

Calls `mcp__chimera__session_consume_handoffs(session_id, cwd)` where:

- `session_id` is your session's chimera id
- `cwd` is your project root (typically `$CLAUDE_PROJECT_DIR` or the
  parent dir of files you've been editing this session)

Same semantics as SessionStart: auto-claims the handoff (first session
to consume becomes owner), renders the directive framing for owned
handoffs, and shows observer view for handoffs another session already
owns. Idempotent — re-running surfaces nothing new for handoffs
you've already consumed.

## When to use

- Another agent told you "I posted a handoff at id=..., go pick it up"
- You started a session, then someone in a sister session posted a
  cwd-scoped handoff to your project, and now you want to pull it in
- Periodically as a sanity check during long sessions, in case something
  drifted in

## When NOT to use

- For "messages targeted at me by name" — use `/inbox` instead. Inbox
  notes and handoffs are different primitives:
  - **Handoffs** = "task for whoever picks up next session in this cwd"
  - **Inbox** = "message addressed to THIS specific session"
- Right after a fresh session boot — the SessionStart hook already
  consumed any pending handoffs into the boot context, so this would
  be a no-op.

## Output

```
📦 chimera handoffs — N directive(s) you now OWN in <cwd>:

- [handoff abc12345 · 2026-05-12T14:30:00 · from def67890]
  <handoff text>

Treat these as directives, not FYIs. Read referenced files, pick the
highest-priority item, propose a first action, and START.
```

Or, if a sister session beat you to the claim:

```
👀 chimera handoffs — N already-claimed handoff(s) in <cwd>:
- [handoff abc12345 · from def67890 · OWNED BY 9d45c212]
  <handoff text>
```

Or if nothing's pending:

```
📭 no new handoffs in scope <cwd> for session <id>.
```
