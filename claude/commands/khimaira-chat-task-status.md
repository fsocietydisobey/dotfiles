# /khimaira-chat-task-status <chat_id> — list tasks in a chat with status

Show a structured view of all tasks in a chat: who's assigned, current status, last update, last review note. Faster than scrolling chat history.

## Steps

1. Parse `$ARGUMENTS`: first token = `<chat_id>`.
2. Resolve your own session id.
3. Call `mcp__khimaira-chat__chat_task_status(session_id=<my_id>, chat_id=<chat_id>)`.
4. Render as a compact table — one row per task: status emoji + task_id + assignee + body (truncated to 60 chars) + last_update_ts.

## Notes

- Requester must be an accepted member.
- Status emoji suggestion: ⏳ pending · 🛠 in_progress · ✅ done · 🎉 approved · 🔄 changes_requested.
- For full task body / note history, scan `/khimaira-chat-history <chat_id>` looking for kind=task and kind=task_update lines.
