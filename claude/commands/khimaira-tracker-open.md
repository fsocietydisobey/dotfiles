# /khimaira-tracker-open [chat_id] — show only the Open section of STATE.md

Extract and render just the `## ☐ Open` section from the tracker's STATE.md.

## Steps

1. Parse `$ARGUMENTS`: optional `<chat_id>`. If not provided, call
   `mcp__khimaira-chat__chat_my_chats(session_id=<my_session_id>)` and pick the
   most-recently-active chat (highest `last_message_ts`).

2. **Resolve the STATE.md path** (same logic as `/khimaira-tracker`):
   - Find the tracker session (name matches `*-tracker-*` or `tracker-*`), call
     `mcp__khimaira__session_state(<tracker_name>)` for its `workspace`.
   - If workspace set: `dev = git -C <workspace> config user.name` (fallback `joseph`);
     `project_path = <workspace>/shared-docs/<dev>/STATE.md`
   - `global_path = ~/.local/state/khimaira/chats/<chat_id>/STATE.md`
   - Use `project_path` if workspace found, else `global_path`.

3. If file missing: render `📭 STATE.md not found — tried <project_path> then <global_path>; is tracker bootstrapped?`
4. Otherwise, extract the Open section. Use the loose sed regex that accepts both
   the canonical glyph-prefixed form (`## ☐ Open`) AND legacy plain forms without
   glyphs (`## Open — anything`):
   ```bash
   sed -nE '/^##[[:space:]]+(☐[[:space:]]+)?Open\b/,/^##[[:space:]]/{ /^##[[:space:]]+(☐[[:space:]]+)?Open\b/{ p; b; }; /^##[[:space:]]/d; p }' STATE.md
   ```
   Or use `Read` + filter in context: find the line matching `## ☐ Open` OR `## Open`,
   collect lines until the next `##` heading, discard the boundary headers.
5. If the section is empty (no bullet lines found): render `✅ No open items.`
6. Otherwise: render the extracted section with its heading.

## Notes

- "Open" means unstarted/backlog items that haven't been assigned yet.
- For in-flight tasks (assigned + in progress), use `/khimaira-tracker` (full state).
- For stale in-flight tasks, use `/khimaira-tracker-stale`.
