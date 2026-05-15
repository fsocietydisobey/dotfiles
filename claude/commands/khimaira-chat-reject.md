# /khimaira-chat-reject [chat_id] — decline a chat invite

Decline a pending invite. Your member-state moves to `rejected`; the chat continues for everyone else. The creator can re-invite you later if they want.

**chat_id is optional** — if omitted, rejects the most recent pending invite. The common case (you just saw an invite block and want to dismiss it).

## Steps

1. Parse `$ARGUMENTS`: if a `<chat_id>` is given, use it. Otherwise leave it None — the MCP tool resolves "latest pending."
2. Resolve your own session id.
3. Call `mcp__khimaira-chat__chat_reject(session_id=<my_id>, chat_id=<chat_id>)` (omit chat_id if not provided).
4. Print confirmation: `🙅 declined <chat_id>`. If response is `{"error": "no pending invites to reject"}`, surface that — there was nothing to decline.

## Notes

- Rejected ≠ left. Reject is for invites you never accepted; leave is for chats you joined and now want out of.
- After rejecting, you stop receiving the invite-channel notification, but the chat record persists with your state recorded. If the creator invites you again, you go back to `pending` and the cycle repeats.
