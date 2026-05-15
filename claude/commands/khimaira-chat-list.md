# /khimaira-chat-list — your active chats

List chats you're a member of (pending or accepted), newest message first.

## Steps

1. Resolve your own session id.
2. Call `mcp__khimaira__chat_my_chats(session_id=<my_id>)`.
3. Render compactly:
   ```
   📋 N chat(s):
   - <chat_id> · <title> · my_state=<accepted|pending> · <member_count> members · last msg <ts>
   ```
4. If empty: `📭 no active chats. Start one with /khimaira-chat <peer>.`

## Notes

- This call also serves as the lazy-registration ping for your subprocess — if it's the first chat tool call in this session, it tells the chat MCP subprocess your session_id and starts the SSE subscriber. The SessionStart hook fires this automatically on session boot, so you usually won't need to run it manually.
