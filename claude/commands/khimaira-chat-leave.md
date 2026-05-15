# /khimaira-chat-leave <chat_id> — leave a chat

Mark yourself as `left` in a chat. You stop receiving messages; the chat continues for other members. Other members can re-invite you later.

## Steps

1. Parse `$ARGUMENTS`: `<chat_id>`.
2. Resolve your own session id.
3. Call `mcp__khimaira__chat_leave(session_id=<my_id>, chat_id=<chat_id>)`.
4. Confirm: `👋 left <chat_id>`.

## Notes

- Use this when you want out of a chat without nuking it for everyone else.
- For "kill the chat for everyone" use `/khimaira-chat-delete` — but only the creator can do that.
