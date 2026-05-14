# /inbox [session_id_or_name] — read pending notes + incoming questions

Manual check of everything in your queue. Default = your current session. Pass an optional session_id or friendly name (e.g. `/inbox khimaira-builder`) to peek at a different session's queue without affecting your own.

Surfaces two distinct surfaces in one view:

1. **Notes** — unread items other sessions have posted: `answer` notes (replies to your questions) and `notice` notes (FYI/ack one-way messages).
2. **Incoming questions** — open questions other sessions have targeted at you, awaiting your answer.

The UserPromptSubmit hook auto-surfaces both on every turn — `/inbox` is a manual escape hatch for an explicit "drain and show me" check, or to confirm nothing is queued.

## Steps

1. Resolve the target session id:
   - If `$ARGUMENTS` is non-empty, use it as-is. It may be a UUID or a friendly name; the daemon resolves both.
   - Otherwise, resolve the current session id from this conversation's earlier turns. If you don't know it, call `mcp__khimaira__session_list()` and pick the most recently-active entry that matches this conversation's file touches.

2. **Pull both surfaces in parallel** (one batch, two MCP calls):
   - `mcp__khimaira__session_pending_notes(session_id=<id>, mark_read=true)` — answers + notices
   - `mcp__khimaira__session_incoming_questions(session_id=<id>)` — open questions targeted at this session

3. Render the result. Four cases:

   - **Both empty**: `📭 inbox empty.` (single line)
   - **Notes only, no questions**: render notes section (see below).
   - **Questions only, no notes**: render questions section (see below).
   - **Both populated**: render notes section first, then questions section, separated by a blank line.

   **Notes section** — header `📬 notes:`, then one entry per note:
     - `kind` — `"answer"` or `"notice"`.
     - `from_session_id` — who sent it (truncate to 8 chars for display).
     - For `kind="answer"`: body is in the `answer` field; `question_text` is the question being answered (render as `re Q: ...` line if present).
     - For `kind="notice"`: body is in the `text` field; no question association.
     - `id` — the 12-char hex note id (useful if user asks "tell me more about that one").
     - NEVER report a note as "empty body" — if `answer` is missing for an answer-kind, fall back to `text`. If both are missing, flag it as a real bug.

   **Questions section** — header `❓ incoming questions:`, then one entry per question:
     - `question_id` — 12-char hex (the handle for `session_post_answer`).
     - `from_session_id` — asker (truncate to 8 chars).
     - `text` — the question body (wrap to keep compact).
     - For each, hint the user: `→ answer with session_post_answer(question_id="...", ...)` so the action is obvious.

4. If a note answers an open question with actionable next steps, OR an incoming question has a clear answer the agent can produce from session context, summarize the action at the bottom: `Next: <thing to do>`. Otherwise no summary.

## Notes

- `mark_read=true` is the right default for the notes path — the user is consciously checking. The auto-inject hook uses a different path (`/inbox/surface`) that peeks without consuming, so /inbox draining doesn't affect future hook injections.
- `session_incoming_questions` does NOT mark questions as answered — that only happens when you call `session_post_answer`. So `/inbox` is safe to invoke repeatedly without losing pending questions.
- This command is read-only with respect to your work — it only mutates the read state of notes. To reply, log a new question (`session_log_question`) directed at the other session, or post an answer to one of their open questions (`session_post_answer`), or send a one-way FYI via `session_post_notice`.
- If the khimaira daemon isn't reachable (`session_list` fails), report the failure plainly — don't silently skip.

## Why both surfaces matter

Notes and incoming questions are deliberately separate primitives (different lifecycles: notes are fire-and-forget read-once; questions have a reply contract). But from the user's mental model, both are "stuff queued for me to handle." A `/inbox` that only checks notes lies by omission — it reports "empty" while questions sit on the questions surface waiting. The auto-surface hook checks both for that reason; this slash command does too.

## When the user passes something that's not an inbox

If `$ARGUMENTS` looks like a 12-char hex (note id) or doesn't match any session_id/name, the user probably meant a different primitive. Inbox notes don't have user-facing IDs you'd type at the command line — note IDs surface internally for `session_ack_notes`. The hex they typed is more likely:

- A **decision id** (12-char hex) — these live on `session_state(<session>)`, not in inboxes. Suggest `/notes <session>` instead.
- A **question id** — also on session_state.

When the resolution fails, render: "📭 inbox empty for `<arg>` — note: `<arg>` looks like a 12-char ID, which is typically a decision/question id (visible via `/notes <session>`), not an inbox key. /inbox takes a session_id or session name."
