# /inbox — read pending answers from other chimera sessions

Manual check of this session's chimera inbox. Surfaces unread answers other parallel sessions have posted via `session_post_answer`.

The UserPromptSubmit hook auto-fetches the inbox on every turn — `/inbox` is a manual escape hatch when you want to peek without typing a real prompt, or to confirm an empty inbox.

## Steps

1. Resolve the current session id. If you don't already know it from this conversation's earlier turns, call `mcp__chimera__session_list()` and pick the most recently-active entry that matches this conversation's file touches.
2. Call `mcp__chimera__session_pending_notes(session_id=<id>, mark_read=true)`.
3. Render the result:
   - If empty: "📭 inbox empty."
   - If non-empty: list each note with `from_session_id`, `kind`, `question_text` (if present, the question being answered), and the answer body. Keep it compact — no headers per note unless there are >3.
4. If a note answers an open question with actionable next steps, summarize the action in one sentence at the bottom: "Next: <thing to do>". Otherwise no summary.

## Notes

- `mark_read=true` is the right default. The auto-inject hook also reads with mark_read=true, so manually re-checking with `/inbox` after a turn won't re-surface the same notes.
- This command is read-only. It does NOT post replies. To reply, log a new question (`session_log_question`) directed at the other session, or post an answer to one of their open questions (`session_post_answer`).
- If the chimera daemon isn't reachable (`session_list` fails), report the failure plainly — don't silently skip.
