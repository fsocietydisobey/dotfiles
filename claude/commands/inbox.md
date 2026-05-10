# /inbox [session_id_or_name] — read pending notes from a chimera session

Manual check of an inbox. Default = your current session. Pass an optional session_id or friendly name (e.g. `/inbox chimera-builder`) to peek at a different session's inbox without affecting your own.

Surfaces unread items other parallel sessions have posted — both `answer` notes (replies to questions you asked via `session_post_answer`) and `notice` notes (FYI/ack via `session_post_notice`).

The UserPromptSubmit hook auto-fetches the inbox on every turn — `/inbox` is a manual escape hatch for an explicit "drain and show me" check, or to confirm an empty inbox.

## Steps

1. Resolve the target session id:
   - If `$ARGUMENTS` is non-empty, use it as-is. It may be a UUID or a friendly name; the daemon resolves both.
   - Otherwise, resolve the current session id from this conversation's earlier turns. If you don't know it, call `mcp__chimera__session_list()` and pick the most recently-active entry that matches this conversation's file touches.
2. Call `mcp__chimera__session_pending_notes(session_id=<id>, mark_read=true)`.
3. Render the result:
   - If empty: "📭 inbox empty."
   - If non-empty: list each note. Each note dict has these fields you should render:
     - `kind` — `"answer"` or `"notice"`. Determines which body field holds the content.
     - `from_session_id` — who sent it (truncate to 8 chars for display)
     - For `kind="answer"`: body is in the `answer` field; `question_text` field is the question being answered (render as "re Q: ..." line if present)
     - For `kind="notice"`: body is in the `text` field; no question association
     - `id` — the 12-char hex note id (useful if user asks "tell me more about that one")
   - Render compactly — one note per few lines, body indented. NEVER report a note as "empty body" — if `answer` is missing for an answer-kind, fall back to `text`; for notices, the body is always `text`. If both are missing, that's a real bug worth flagging.
4. If a note answers an open question with actionable next steps, summarize the action in one sentence at the bottom: "Next: <thing to do>". Otherwise no summary.

## Notes

- `mark_read=true` is the right default for explicit `/inbox` invocations — the user is consciously checking. The auto-inject hook uses a different path (`/inbox/surface`) that peeks without consuming, so /inbox draining doesn't affect future hook injections.
- This command is read-only. It does NOT post replies. To reply, log a new question (`session_log_question`) directed at the other session, or post an answer to one of their open questions (`session_post_answer`), or send a one-way FYI via `session_post_notice`.
- If the chimera daemon isn't reachable (`session_list` fails), report the failure plainly — don't silently skip.

## When the user passes something that's not an inbox

If `$ARGUMENTS` looks like a 12-char hex (note id) or doesn't match any session_id/name, the user probably meant a different primitive. Inbox notes don't have user-facing IDs you'd type at the command line — note IDs surface internally for `session_ack_notes`. The hex they typed is more likely:

- A **decision id** (12-char hex) — these live on `session_state(<session>)`, not in inboxes. Suggest `/notes <session>` instead.
- A **question id** — also on session_state.

When the resolution fails, render: "📭 inbox empty for `<arg>` — note: `<arg>` looks like a 12-char ID, which is typically a decision/question id (visible via `/notes <session>`), not an inbox key. /inbox takes a session_id or session name."
