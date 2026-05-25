# /khimaira-tracker-digest [chat_id] — request a synthesized digest from tracker-1

Post `@tracker digest` to the active roster chat and prompt tracker-1 to reply with
a synthesized summary (STATE.md contents + analysis). Tracker responds in the chat
within ~30s.

## Steps

1. Parse `$ARGUMENTS`: optional `<chat_id>`. If not provided, call
   `mcp__khimaira-chat__chat_my_chats(session_id=<my_session_id>)` and pick the
   most-recently-active chat (highest `last_message_ts`).
   (Path resolution note: digest round-trips through tracker; tracker reads STATE.md from
   the correct project or global path per its bootstrap brief — no local path needed here.)
2. Send the digest request:
   `mcp__khimaira-chat__chat_send(session_id=<my_session_id>, chat_id=<chat_id>, body="@tracker digest")`
3. Tell the user:
   ```
   📤 Posted @tracker digest to <chat_id>.
   Tracker will reply in the chat within ~30s.
   Read the reply with /khimaira-chat-history <chat_id> 5
   ```
4. Optionally: wait for tracker's reply by calling
   `mcp__khimaira-chat__chat_history(session_id=<my_session_id>, chat_id=<chat_id>, limit=5)`
   after a brief pause, and render tracker's response if it has arrived.

## Notes

- Tracker's digest contains: STATE.md rendered + any anomalies it noticed. If you just
  want the raw STATE.md without synthesis, use `/khimaira-tracker` instead (local file
  read, no round-trip).
- If tracker-1 is not in this chat (not a roster chat), the `@tracker` ping lands as
  a normal message with no response. Check with `/khimaira-chat-list` to confirm you're
  in the right chat.
- `@tracker` pings are one of tracker's few permitted chat interactions (per tracker.md).
  Don't spam; one digest request per question is enough.
