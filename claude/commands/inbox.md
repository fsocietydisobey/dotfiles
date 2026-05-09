# /inbox — read pending notes from other chimera sessions

Manual check of this session's chimera inbox. Surfaces unread items other parallel sessions have posted — both `answer` notes (replies to questions you asked via `session_post_answer`) and `notice` notes (FYI/ack via `session_post_notice`).

The UserPromptSubmit hook auto-fetches the inbox on every turn — `/inbox` is a manual escape hatch for an explicit "drain and show me" check, or to confirm an empty inbox.

## Steps

1. Resolve the current session id. If you don't already know it from this conversation's earlier turns, call `mcp__chimera__session_list()` and pick the most recently-active entry that matches this conversation's file touches.
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
