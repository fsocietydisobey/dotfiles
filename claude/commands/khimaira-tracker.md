# /khimaira-tracker [chat_id] — pull current STATE.md from the active roster's tracker

Show the full tracker STATE.md for the current (or specified) chat.

## Steps

1. Parse `$ARGUMENTS`: optional `<chat_id>`. If not provided, resolve the current chat:
   call `mcp__khimaira-chat__chat_my_chats(session_id=<my_session_id>)`, pick the entry
   with the highest `last_message_ts`.

2. **Resolve the STATE.md path** (project-scoped vs chat-scoped):
   - Find the tracker session: scan `chat_my_chats` members or `chat_history` for a session
     whose name matches `*-tracker-*` or `tracker-*`. Call
     `mcp__khimaira__session_state(<tracker_name>)` to get its `workspace` field.
   - If `workspace` is set (project-scoped roster):
     - `dev` = run `Bash("git -C <workspace> config user.name")` (fallback: `joseph`)
     - `project_path` = `<workspace>/shared-docs/<dev>/STATE.md`
   - `global_path` = `~/.local/state/khimaira/chats/<chat_id>/STATE.md`
   - Try `project_path` first (if workspace was found); else use `global_path`.

3. Read the resolved path with the `Read` tool.

4. If missing: render:
   ```
   📭 STATE.md not found.
   Tried: <project_path>
   Fallback: <global_path>
   This roster is project-scoped — tracker should be writing STATE.md to the project
   codebase. If tracker hasn't bootstrapped yet, ping them:
   chat_send(chat_id, body="@tracker bootstrap your STATE.md now")
   ```
   (Show only the paths actually tried; omit project_path line if roster is chat-scoped.)

5. Otherwise: render the file contents directly to the user (it's already markdown).

## Notes

- STATE.md is updated silently by tracker-1 after every master approval. It is NOT
  updated in real time — it reflects the last tracker write, typically within seconds
  of an event.
- For a synthesized digest (with analysis), use `/khimaira-tracker-digest` instead.
- For just open items, use `/khimaira-tracker-open`.
