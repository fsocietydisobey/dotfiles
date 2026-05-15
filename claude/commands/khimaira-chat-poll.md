# /khimaira-chat-poll <chat_id> — manual catch-up via pull (escape hatch)

Pure-pull check for new messages in a chat. Use when channels seem broken — research-preview protocol drift, MCP transport hiccup, daemon momentarily unreachable. Reads `chat_history(since=<last_seen>)` and renders any new messages inline.

## When to use

- Channels delivery seems silent: you sent something, peer didn't react.
- After a daemon restart, to confirm you didn't miss anything.
- Debugging.

For normal real-time use, you don't need this — channel notifications land automatically as `<channel>` blocks.

## Steps

1. Parse `$ARGUMENTS`: `<chat_id>`.
2. Resolve your own session id.
3. Find your last-seen `event_id` for this chat: best-effort check the conversation transcript for the most recent `<channel chat_id="<chat_id>" msg_id="...">` block; use that `msg_id`. If unknown, omit the `since` arg and pull the last 50 messages.
4. Call `mcp__khimaira__chat_history(session_id=<my_id>, chat_id=<chat_id>, since=<last_msg_id_or_None>, limit=50)`.
5. Render each returned message: `[<ts> · <sender_name>] <body>`. If empty: `📭 nothing new since <last_event_id>`.

## Notes

- This doesn't restart the SSE subscription — channels keep working in the background. This is a one-shot catch-up, not a switch to polling.
- If you want continuous polling (channels truly down), use `/loop 30s /khimaira-chat-poll <chat_id>` — but flag it as a workaround and stop the loop once channels recover.
