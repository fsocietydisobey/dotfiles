# /khimaira-chat-auto-accept <peer1,peer2,...> — set this session's auto-accept allowlist

Configure which peers' invites should skip the handshake (`pending → accepted` directly). Useful when a trusted master session frequently spins up worker chats with this session — saves the manual `/khimaira-chat-accept` step every time.

## Steps

1. Parse `$ARGUMENTS`: comma-separated session names or UUIDs (no spaces). Pass an empty value to clear.
2. Resolve your own session id.
3. Call `mcp__khimaira-chat__chat_auto_accept_from(session_id=<my_id>, allow=<list>)`.
4. Print confirmation: `🤝 auto-accept allowlist: <names>` (or `🤝 auto-accept cleared` if empty).

## Notes

- Allowlist is **REPLACED**, not extended. Pass the full desired list each time.
- Matching is by session UUID OR friendly name — either form works.
- Persisted at `~/.local/state/khimaira/chats/auto-accept-<session_id>.json` (survives session restarts).
- Trust model: anyone in the list can drop you into a chat without warning. Use sparingly — appropriate for sessions YOU spawned (master/agent), risky for sessions you don't fully control.

## Examples

```
/khimaira-chat-auto-accept master-bot,reviewer-bot
   → auto-accept allowlist set: [master-bot, reviewer-bot]

/khimaira-chat-auto-accept
   → auto-accept cleared (back to manual accept-everything)
```
