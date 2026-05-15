# /khimaira-chat-task-update <chat_id> <task_id> <status> [note...] — move a task through its lifecycle

Update a task's status. Valid transitions:
- pending → in_progress → done (any accepted member, if they're the assignee)
- done → approved (creator only)
- done → changes-requested (creator only)

## Steps

1. Parse `$ARGUMENTS`: `<chat_id>`, `<task_id>`, `<status>`, optional `<note>` (rest of args).
2. Resolve your own session id.
3. Call `mcp__khimaira-chat__chat_task_update(session_id=<my_id>, chat_id=<chat_id>, task_id=<task_id>, new_status=<status>, note=<note>)`.
4. Print confirmation showing new status. On 403 (wrong role for transition): surface the error.

## Notes

- The status update is itself a chat message visible to all accepted members — implicit audit trail.
- If you got "changes-requested" as assignee, you can move it back to `in_progress` and resubmit when ready.
