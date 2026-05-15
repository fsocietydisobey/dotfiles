# /khimaira-chat-send-to <chat_id> <recipients> <body...> — private message to subset of chat members

Like `/khimaira-chat-send` but only the listed recipients receive the channel push. Other members can still see the message via `chat_history` — `to` controls **push delivery**, not durable visibility.

## Steps

1. Parse `$ARGUMENTS`:
   - First token = `<chat_id>`
   - Second token = `<recipients>` — comma-separated session names or UUIDs (no spaces inside the list, e.g. `agent-a,agent-b`)
   - Everything after = body
2. Resolve your own session id.
3. Call `mcp__khimaira-chat__chat_send_to(session_id=<my_id>, chat_id=<chat_id>, body=<body>, to=<recipients-list>)`.
4. Print confirmation: `🔒 sent to <recipients> in <chat_id>`.

## When to use

- Master sidebars an agent on a task without broadcasting to siblings
- Two members coordinate a sub-thread inside a multi-party chat
- Pair-programming-style focus inside a larger group

## When NOT to use

- For true confidentiality (encrypted-at-rest, removed from history) — that's a separate `confidential=True` feature not yet built. `to` is push-routing only; the message persists in the JSONL transcript visible to all accepted members via `chat_history`.
- For broadcast — use `/khimaira-chat-send` (no recipients arg means everyone).
