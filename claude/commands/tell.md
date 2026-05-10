# /tell <session_or_name> <message> — fire-and-forget notice to another session

Sends a one-way FYI / ack to another chimera session. Wraps `mcp__chimera__session_post_notice` with sensible defaults so the user doesn't have to choose between primitives.

Use for:
- "FYI I went with option C"
- "starting from commit X, watch for Y"
- "thanks, landed"
- Any "you don't need to reply" cross-session note

For "I'm leaving a note for whoever opens the next chat in this project" use `/handoff` instead.
For "I need an answer back" use `/ask`.

## Steps

1. `$ARGUMENTS` should be `<session_or_name> <message>`. Parse:
   - First whitespace-separated token = target session id or friendly name
   - Everything after = message body
   - If `$ARGUMENTS` doesn't have at least 2 tokens, render: "Usage: `/tell <session_or_name> <message>`. The first token is the target session; the rest is the body. For a note to a future session that doesn't exist yet, use `/handoff` instead."

2. Resolve the current session id (your sender id). Use the session_id from this conversation's earlier turns — the SessionStart hook surfaces it as `🆔 chimera session_id: <uuid>`. If unsure, call `mcp__chimera__session_list` and pick the most-recently-active entry matching this conversation's recent file touches.

3. Call `mcp__chimera__session_post_notice(target_session_id=<first_token>, text=<rest>, from_session_id=<my_session_id>)`.

4. On success: print `📨 sent to <target>` and the note id from the response.

5. **On failure with "no session named or id'd"**: don't just relay the error. The target doesn't exist. Suggest the right alternative:
   ```
   ❌ no session named '<target>' yet.
   If they're just about to spin up: tell them to run
       mcp__chimera__session_set_name(<their_uuid>, "<target>")
   on their first turn, then re-run /tell.
   If you want the message to land for ANY future session in a
   project's working directory, use /handoff instead.
   ```

## Notes

- Notice notes auto-expire after 3 surfaces if the recipient agent never explicitly acks them — won't loop forever even if ignored.
- This is the right command 80% of the time. The other 20%: handoffs (target doesn't exist yet), questions (need an answer back), decisions (note for yourself).
