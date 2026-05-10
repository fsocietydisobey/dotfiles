# /handoff [scope_cwd] <message> — leave a note for any future session in this project

Drops a handoff note that auto-surfaces on the SessionStart hook of any future Claude session whose working directory matches `scope_cwd`. Wraps `mcp__chimera__session_post_handoff` with sensible defaults so the user doesn't have to think about which primitive to use.

Use for:
- "HANDOFF: shipped X, pickup at Y, watch for Z" — at the end of a working session
- "FYI to anyone in this project: env var FOO must be set"
- "Next session: do task A before task B"
- Any forward-looking note when you don't know who will pick it up

For "tell a SPECIFIC session something" (when the target is named/known) use `/tell` instead.
For "ask a session and wait for an answer" use `/ask`.

## Behavior

The handoff:
- Stays in `~/.local/state/chimera/handoffs.jsonl` for 7 days by default (`expires_in_hours=168`).
- Auto-surfaces on the SessionStart hook of any future session whose `cwd` is `scope_cwd` OR a child path of it.
- Each future session sees the handoff exactly once (read-tracking by session_id; resumes don't re-surface).
- Multiple future sessions in the same cwd EACH see it (multi-recipient).

## Steps

1. Parse `$ARGUMENTS`:
   - If first whitespace-separated token is an absolute path (starts with `/`) AND exists or looks pathlike, treat it as `scope_cwd`. Rest of args = message.
   - Otherwise: `scope_cwd` defaults to the calling agent's current working directory (use Bash `pwd` to resolve, or read from environment if shell tool isn't appropriate). Whole `$ARGUMENTS` = message.
   - If `$ARGUMENTS` is empty, render:
     ```
     Usage: /handoff [scope_cwd] <message>
     Drops a forward-looking note any future session in scope_cwd will read.
     If scope_cwd is omitted, uses the current working directory.
     Examples:
       /handoff "shipped tasks #58-#65; pickup at workspaces/IMPLEMENTATION.md"
       /handoff /home/user/work/jeevy_portal "next session: run npm install"
     ```

2. Resolve your own session id (sender). Use SessionStart hook value; fall back to `mcp__chimera__session_list`.

3. Call `mcp__chimera__session_post_handoff(from_session_id=<my_id>, text=<message>, scope_cwd=<resolved_cwd>)`.

4. Print confirmation:
   ```
   📦 handoff posted (id=<id>) — any future session in <scope_cwd> will see it on SessionStart
      expires in 7d (168h)
   ```

5. If the user wants a custom expiration, they can say `/handoff --hours 24 <message>` (parse the flag before scope detection). 24h is good for time-bounded asks; 168h (default) for "permanent context."

## Notes

- This is the right tool for "leaving notes for sessions that don't exist yet." The wrong tools are (a) `session_post_notice` to a session that hasn't been named yet (404s), and (b) `session_log_decision` (only visible on explicit pull, not auto-surfaced).
- Multi-recipient by design: all future sessions in scope see the handoff once each. Don't use this for "tell one specific session" — use `/tell <name>` for that.
- The handoff body becomes part of the new session's first context block. Be terse: title + 2-3 lines of pickup pointers + file paths. No screenshots or tool outputs.
