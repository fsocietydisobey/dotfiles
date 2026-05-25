# /agent-ready — agent-side: confirm budget compliance for a pending /khimaira-assign task

Replaces having to type `ready [task-id: <long-uuid>]` manually. Looks up the pending task
assignment addressed to this session, reads `~/.claude/settings.json`, verifies model+effort
match the assignment's requirements, and sends the ack to master automatically.

## When to use

- You received a `🔔 TASK ASSIGNMENT` block from master via SSE
- You've set the required `/model` and `/effort` in this window
- You're ready to ack and wait for the 🟢 begin signal

## Steps

1. **Resolve my session id** — from SessionStart context block (🆔 line).

2. **Find the most recent pending assignment** addressed to me:
   - Call `mcp__khimaira-chat__chat_my_chats(session_id=<my_id>)` → list of chats I'm in.
   - For each chat (newest first), call `mcp__khimaira-chat__chat_history(session_id=<my_id>, chat_id=<chat_id>, limit=30)`.
   - Walk the messages newest-first. Find the most recent message where:
     - `body` starts with `🔔 TASK ASSIGNMENT [task-id: ...]`
     - `to` array contains my session_id (assignment targeted at me)
     - I haven't already acked it (no later message from me with `✅ ready [task-id: <same>]`)
   - Extract from the body:
     - `task_id` (regex: `task-id: (task-[a-f0-9]+)`)
     - `required_model` (regex on the `/model <X>` line in the "Required budget" section)
     - `required_effort` (regex on the `/effort <Y>` line)
   - Remember the `chat_id` for the ack send.

3. **If no pending assignment found**: print
   ```
   ⚠️ No pending task assignment found for this session.
   Either: no assignment was sent, or you've already acked it, or you're in a chat where
   master used `chat_send` (broadcast) instead of `chat_send_to` (targeted) — in that case
   you need to ack manually with: chat_send "✅ ready [task-id: <id>] | model=<X> effort=<Y>"
   ```
   Stop.

4. **Read ~/.claude/settings.json** — use the Read tool, parse JSON.

5. **Check compliance**:
   - `current_model`: settings.json `.model` field. If absent → defaults to Opus 4.7.
     Normalize: "opus" matches any opus variant, "sonnet" any sonnet, "haiku" any haiku.
   - `current_effort`: settings.json `.effortLevel` field. Compare directly to `required_effort`.

6. **If compliant** — send ack via chat:
   Call `mcp__khimaira-chat__chat_send(session_id=<my_id>, chat_id=<chat_id>, body="✅ ready [task-id: <task_id>] | model=<required_model> effort=<required_effort>")`.
   Then print in window:
   ```
   ✅ Acked master for task <task_id>.
   Budget verified: model=<required_model>, effort=<required_effort>.
   Waiting for 🟢 ALL AGENTS CONFIRMED — BEGIN signal before starting work.
   ```

7. **If non-compliant** — do NOT ack. Print exactly what's still wrong:
   ```
   ⚠️ Budget mismatch for task <task_id>:
     Required:  model=<required_model>, effort=<required_effort>
     Current:   model=<current_model>, effort=<current_effort>

   Run the missing slash commands, then `/agent-ready` again:
     <list only the ones that don't match: `/model <required_model>` and/or `/effort <required_effort>`>
   ```
   Stop. Do not send anything to chat.

## Notes

- This is the agent-side counterpart to master's `/khimaira-assign`. The pairing closes the
  type-task-id-by-hand UX gap.
- The skill never starts work — that only happens on receipt of the `🟢 BEGIN` block from master.
- If multiple pending assignments exist (rare), the most recent one wins. If you need to ack
  an older assignment, do it manually with `chat_send`.
- The settings.json read is a legitimate gate-verification action — distinct from the pre-read
  reflex violation banked earlier. Pre-reading before the user types ready/runs this skill is
  the violation; reading AT ready (via this skill) is the protocol.
