# /listen [name] — register this session as an agent available for delegation

The master/agent pattern: one "master" Claude Code session leads a work block; N "agent" sessions register themselves as listening. The master calls `/delegate` to fan out tasks; each agent's hook surfaces the incoming question on its next turn; agent answers; master collects.

This command makes the current session an agent.

## Steps

1. **Parse `$ARGUMENTS`** — the desired friendly name (e.g. `agent-1`, `research-bot`). If empty, default to `agent-<8-char-prefix-of-current-session-id>`.

2. **Resolve current session id** — from the SessionStart hook context, or `mcp__khimaira__session_list()` fallback (most-recently-active entry that matches this conversation's file touches).

3. **Set the name** — call `mcp__khimaira__session_set_name(session_id=<my-id>, name=<parsed-name>)`. Idempotent — re-running with the same name is a no-op.

4. **Set listening status** — call `mcp__khimaira__session_set_status(session_id=<my-id>, status="listening", detail="available for master delegation")`.

5. **Render the confirmation**:
   ```
   📡 listening as `<name>` (session_id=<8-char-prefix>)
   master can delegate via `/delegate <name> <task>` from its window.
   ```

6. **Briefly explain the contract** to the user so they know what happens next:
   - When the master fires a task targeting this agent, the question lands in this session's inbox.
   - On the next prompt the user types in this window, the UserPromptSubmit hook surfaces the question.
   - The agent (me) does the work and answers via `session_post_answer`.
   - Until the user types something here, the question sits unread — master will time out after 15 min by default.

## Notes

- Listening is advisory — master can delegate to any named session, listening or not. The status is just a hint.
- To stop listening, set status back to `idle` or just close the session.
- The same session can listen + do other work — `/listen` doesn't restrict what else this session does.
