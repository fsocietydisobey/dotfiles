# /khimaira-session-logs — Look up another khimaira session by name or id

Fetch the externalized state of another Claude Code session — its decisions, file touches, open questions, and status — without interrupting the working session.

## Steps

1. Parse `$ARGUMENTS` as the session handle:
   - If empty: call `mcp__khimaira__session_list` and report all active sessions, sorted newest-first. Stop there — let the user pick.
   - Otherwise: treat $ARGUMENTS as a session name (e.g. `khimaira-monitor`, `jeevy-auth-fix`) OR a UUID. The khimaira tools resolve either.
2. Call `mcp__khimaira__session_state` with `session_id=$ARGUMENTS`. Name resolution happens server-side — most-recently-active wins on name collisions.
3. Report the digest in this shape:
   - **Header line**: name, status, last activity age.
   - **Recent decisions** (latest 5): `decision text` + ` — why` (truncate why at 200 chars).
   - **Recent file touches** (latest 5): path, line range if any, summary.
   - **Open questions**: each as `(id=...) text` with the line `→ answer with mcp__khimaira__session_post_answer(target_session_id="<that-session>", question_id="...", answer="...")`.
4. If there are open questions and the current conversation already has an obvious answer to one, offer to post the answer (don't auto-post — confirm with the user first).
5. If the session has been idle >30 min, flag it: `⏸ idle 35m — may not be actively listening`.

## Examples

- `/khimaira-session-logs khimaira-builder` — look up by friendly name
- `/khimaira-session-logs ceae577d-78b2-46b9-b2a9-4ebebfa21852` — look up by UUID
- `/khimaira-session-logs` (no arg) — list all sessions

## Notes

- This is read-only by default. Do not call `session_post_answer`, `session_log_decision`, or any other write tool unless the user asks.
- For a richer dashboard view, the same data is at `http://127.0.0.1:8740/api/sessions/<id-or-name>` — point the user there if they want raw JSON.
- Session names live in `status.json`'s `name` field, set by the target session's first-turn `mcp__khimaira__session_set_name` call.
