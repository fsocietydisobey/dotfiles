# /khimaira-chat-delete <chat_id> — archive a chat (creator only)

Move the chat's JSONL to `~/.local/state/khimaira/chats/archive/`. Other members stop receiving messages; history is preserved on disk.

**Permission rule**: only the chat's creator can delete. Non-creators get 403; use `/khimaira-chat-leave` to remove yourself instead.

## Steps

1. Parse `$ARGUMENTS`: `<chat_id>`.
2. Resolve your own session id.
3. Call `mcp__khimaira__chat_delete(session_id=<my_id>, chat_id=<chat_id>)`.
4. Confirm: `🗑️ archived <chat_id> → <archived_to>`.

## Notes

- Archived chats can be recovered manually by moving the file back into `~/.local/state/khimaira/chats/`.
- This is intentionally a soft-delete to prevent hostile actors in a group from nuking history.
