# /ask <session_or_name> <question> — synchronous cross-session ask

Asks another khimaira session a question and waits for the answer in the same turn. Wraps the two-step pattern `mcp__khimaira__session_log_question(target=...)` + `mcp__khimaira__session_wait_for_answer(...)` so the user doesn't have to remember both.

Use for:
- "Does the spec at <path> say X or Y?" — when the other session has codebase context you don't
- "Confirm before I proceed: was the deprecation done in commit Z or earlier?"
- "What value should I use for <config_key>?"

For "FYI no reply expected" use `/tell` instead.
For "leave a note for whoever opens the next chat" use `/handoff`.

## Behavior

This command BLOCKS the current turn until the other session answers OR a 5-minute timeout fires. The user sees nothing until the answer comes back. They'll need to wake the target session by typing in its window — at that point its hook surfaces the question, the agent answers, and this turn unblocks with the answer in hand.

Default timeout: 300 seconds. Override with `--timeout <seconds>` (e.g. `/ask --timeout 60 khimaira-builder "..."`).

## Steps

1. Parse `$ARGUMENTS`:
   - Optional leading `--timeout <N>` flag
   - First non-flag token = target session id or friendly name
   - Everything after = the question body
   - If parse fails, render: "Usage: `/ask [--timeout SECONDS] <session_or_name> <question>`. Default timeout is 300s. The target session needs to be woken (user types in its window) for the answer to flow back."

2. Resolve your own session id (sender). Use the value the SessionStart hook surfaced; fallback to `mcp__khimaira__session_list` if unknown.

3. Call `mcp__khimaira__session_log_question(session_id=<my_id>, text=<question>, target_session_id=<target>)`. Capture the returned question id.

4. Call `mcp__khimaira__session_wait_for_answer(session_id=<my_id>, question_id=<id>, timeout=<timeout>)`.

5. **On answer**: print the answer body verbatim. Prefix with `✅ <target>:` so the user sees who answered. Include any actionable next-step hint at the bottom if the answer suggests one.

6. **On timeout**: print `⏱️ /ask timed out after <N>s — target session likely wasn't woken. The question is still open as q=<id>; it'll surface in <target>'s next prompt either way.` Don't treat this as an error — the question is still pending.

7. **On unresolvable target**: same fallback message as `/tell` — suggest `session_set_name` for sessions about to spin up, or `/handoff` if the target doesn't exist yet.

## Notes

- BLOCKING: don't `/ask` casually. If the target session isn't actively running and won't be woken soon, the turn just times out wastefully. Use `/tell` for things that don't need an answer right now.
- 300s default is generous. Most cross-session asks resolve in <60s once you wake the target.
- If you don't need the answer in the SAME turn (just want to leave a question), use `mcp__khimaira__session_log_question` directly — it's the non-blocking version.
