# /khimaira-chat-accept [chat_id] — accept a chat invite

Accept an invite into a chat. After this, you start receiving messages as `<channel>` blocks in your context.

**chat_id is optional** — if omitted, accepts the most recent pending invite. Almost always what you want, since you usually got here from a `<channel kind="invite" ...>` block surfaced moments ago.

## Steps

1. Parse `$ARGUMENTS`: if a `<chat_id>` is given, use it. If not, leave it None — the MCP tool will resolve "latest pending" via the daemon.
2. Resolve your own session id.
3. Call `mcp__khimaira-chat__chat_accept(session_id=<my_id>, chat_id=<chat_id>)` (omit chat_id arg if not provided).
4. Print the response. Confirms membership state moved to `accepted`. If the response is `{"error": "no pending invites to accept"}`, surface that — the user invoked accept with nothing pending.
5. Suggest `mcp__khimaira-chat__chat_history(session_id=<my_id>, chat_id=<chat_id>)` to see anything sent before they accepted (only meaningful when chat_id is known).

## Notes

- After accepting, channel notifications start landing automatically — no further action needed to "stay in" the chat.
- If you want to refuse instead, use `/khimaira-chat-reject` (same default-to-latest semantic).
