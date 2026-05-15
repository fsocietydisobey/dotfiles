# /khimaira-chat-task <chat_id> [@assignee] <body...> — create a structured task in a chat

Create a task message with status tracking instead of a free-form message. Tasks have a lifecycle (pending → in-progress → done → approved | changes-requested) so the master can track work without scrolling chat history.

## Steps

1. Parse `$ARGUMENTS`:
   - First token = `<chat_id>`
   - Optional `@<assignee>` (session name or UUID prefixed with `@`); if omitted, task is unassigned
   - Everything else = task body
2. Resolve your own session id.
3. Call `mcp__khimaira-chat__chat_task_create(session_id=<my_id>, chat_id=<chat_id>, body=<body>, assignee_session_id=<assignee or None>)`.
4. Print confirmation: `📋 task <task_id> created in <chat_id>` plus assignee if any.

## Notes

- Use this INSTEAD of a free-form chat_send when the message is "do this work and report back."
- Assignee can move pending → in-progress → done themselves. Only the chat creator (master) can approve/changes-requested.
- For ad-hoc messages with no work-tracking, use `/khimaira-chat-send` instead.
