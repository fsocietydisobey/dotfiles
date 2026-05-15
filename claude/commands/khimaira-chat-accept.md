# /khimaira-chat-accept <chat_id> — accept a chat invite

Accept an invite into a chat room. After this, you start receiving messages as `<channel>` blocks in your context.

## Steps

1. Parse `$ARGUMENTS`: first token = `<chat_id>` (e.g., `chat-abc123def456`).
2. Resolve your own session id.
3. Call `mcp__khimaira__chat_accept(session_id=<my_id>, chat_id=<chat_id>)`.
4. Print the response. Confirms membership state moved to `accepted`.
5. Suggest the user check `mcp__khimaira__chat_history(session_id=<my_id>, chat_id=<chat_id>)` to see anything sent before they accepted.

## Notes

- You can only accept a chat you've been invited to. Errors surface from the daemon.
- After accepting, channel notifications start landing automatically — no further action needed to "stay in" the chat.
