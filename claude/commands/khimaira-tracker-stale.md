# /khimaira-tracker-stale [chat_id] — show in-flight tasks with no movement >24h

Surface stale tasks: items in `## ▶ In flight` whose last-update timestamp is older
than 24 hours. Use this to catch tasks that are assigned but silently stuck.

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
4. Read the file. Extract the In-flight section — match either the canonical
   glyph-prefixed form (`## ▶ In flight`) OR the legacy plain form (`## In flight`):
   ```bash
   sed -nE '/^##[[:space:]]+(▶[[:space:]]+)?In[[:space:]]+flight\b/,/^##[[:space:]]/{ /^##[[:space:]]+(▶[[:space:]]+)?In[[:space:]]+flight\b/{ p; b; }; /^##[[:space:]]/d; p }' STATE.md
   ```
   Or use `Read` + filter in context: find the line matching `## ▶ In flight` OR
   `## In flight` (with optional qualifier suffix), collect lines until the next `##`
   heading, discard the boundary headers.
5. For each task entry in that section, find the timestamp (look for patterns like
   `Xm ago`, `Xh ago`, `Xd ago` in the entry text). Parse X as minutes/hours/days.
   - If the most recent timestamp for an entry is > 24h (1440 min): mark it stale.
   - If no timestamp can be parsed: treat as unknown, include with `⚠️ STALE (no timestamp)`.
6. If no stale entries: render `✅ No stale in-flight tasks.`
7. If any stale entries: render them with `⚠️ STALE — ` prefix per entry, e.g.:
   ```
   ⚠️ STALE — task-abc123 (agent-1): "Fix auth bug" — last update 26h ago
   ⚠️ STALE (no timestamp) — task-xyz789 (agent-2): "Refactor DB layer"
   ```

## Notes

- "Stale" is defined as >24h without a state change logged in STATE.md. Observer
  also monitors this independently, but this command gives you a quick pull-mode view.
- If you see unexpected staleness, ping tracker: `/khimaira-tracker-digest` for context.
- Timestamp parsing is best-effort. If STATE.md uses a different format, read the raw
  section and apply judgment.
