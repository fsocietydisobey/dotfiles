# /khimaira-chat-roles — show your role + recommended budget per chat

Inspect your `member_roles` value across all chats you're a member of, plus the v1.4 recommended `/model` + `/effort` for each role. Closes the v1.6.1 visibility gap surfaced after v1.6 shipped: roles are durably tracked in `room.meta.member_roles` (Phase B v2) but there was no purpose-built surface to read them per chat.

## When to use vs alternatives

| Need | Use |
|---|---|
| "What's my role in each chat?" | `/khimaira-chat-roles` (this) |
| "What chats am I a member of?" | `/khimaira-chat-list` |
| "What budget does role X want?" | `docs/khimaira-chat.md#token-cost-budgeting` (canonical table) |
| "Change my role in a chat" | `chat_grant_role` (caller must be master) |

## Args

None. Always lists every accepted chat the caller is in.

## Steps

1. **Resolve own session id** — from SessionStart hook or `session_list()` fallback.

2. **List your chats** — `mcp__khimaira-chat__chat_my_chats(session_id=<my_id>)` → list of chat metadata. Filter to `state == "accepted"`.

3. **Fetch role per chat** — for each accepted chat, call `mcp__khimaira-chat__chat_history(session_id=<my_id>, chat_id=<id>, limit=1)`. The most recent record carries the chat's META; extract `meta.member_roles[<my_id>]`. If `member_roles` is absent (v1-era implicit-master chat), fall back to `meta.created_by == <my_id> ? "master" : "agent"`.

4. **Lookup recommended budget per role** — fixed table (matches `ROLE_BUDGET` constant in `packages/khimaira/src/khimaira/monitor/chats.py`):

```
master    → /model opus,   /effort max
agent     → /model sonnet, /effort medium
observer  → /model haiku,  /effort default
critic    → (no default — orchestrator's discretion based on scope)
```

5. **Render the table** — one row per chat:

```
🎚️ Your roles + recommended budgets

| Chat              | Title                                    | Your role | Budget                  |
|-------------------|------------------------------------------|-----------|-------------------------|
| chat-400516f81475 | v1.4 — model + thinking-mode role-routing| master    | /model opus, /effort max|
| chat-abc123def    | Phase C kickoff                          | agent     | /model sonnet, /effort medium |
| chat-xyz789       | Audit review (read-only)                 | observer  | /model haiku, /effort default |
```

If the chat is currently in deputize mode (`meta.deputized_original_master` is set AND your session id matches it), annotate the row: `master (paused — vice: <vice-name>)`. If your session is currently acting as a vice (`meta.deputized_original_master` is set AND your id is the current master per `member_roles` but NOT the original), annotate: `master (vice — original: <orig-master>)`.

6. **Print a closing tip** — `Type the budget commands in this window to match. Reference: docs/khimaira-chat.md#token-cost-budgeting`.

## When NOT to use

- **Just looking for chat IDs / titles** → `/khimaira-chat-list` is lighter (no per-chat META fetch).
- **Want to CHANGE a role** → `chat_grant_role`; this command only reads.
- **In a non-khimaira project** → no khimaira-chat MCP registered means no chats to enumerate; this command returns empty.

## Notes

- **Read-only**. No writes; no state mutations; safe to run repeatedly.
- **Per-chat fetch cost**: one `chat_history` call per accepted chat. For users with many chats (>20), surface a hint to filter via the standard `/khimaira-chat-list` first if performance matters.
- **Deputize annotation** lives only when the v1.6 `deputized_original_master` field is present on the chat's META — vanilla chats omit the parenthetical role-state annotation.
- **Critic shows blank budget** intentionally (per v1.4 + v1.5 convention — critic depends on scope of work being critiqued, no default).
- **Composes with v1.5 directive emit** — this command shows CURRENT state; v1.5's channel-block directive shows STATE CHANGES. Together they cover both "what role do I hold right now" and "my role just changed, here's what to type."
