# /khimaira-chat-history <chat_id> [limit] — read chat transcript

Show recent messages from a chat you're an accepted member of. Default limit 50, override as second arg.

## Steps

1. Parse `$ARGUMENTS`: `<chat_id>` (required), `<limit>` (optional integer, default 50).
2. Resolve your own session id.
3. Call `mcp__khimaira__chat_history(session_id=<my_id>, chat_id=<chat_id>, limit=<limit>)`.
4. Render each message: `[<ts> · <sender_name>] <body>`. Newest at the bottom.

## Notes

- Only accepted members can read. 403 if you're pending or non-member.
- For "show me only what's new since I last looked", use `/khimaira-chat-poll <chat_id>` (catches up via since-event-id).
