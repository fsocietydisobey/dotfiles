# /khimaira-listen [detail-text] — register this session as listening for delegation pings

Marks the current session as available to receive targeted questions, notices, and delegated tasks from any other session (typically a "master" running `/khimaira-delegate`). Pure status-setter — does NOT rename the session (use `/rename` for that).

## Active-listening modes

Khimaira sessions are user-interaction-driven by default. The session only responds to incoming pings when the user types in this window — its UserPromptSubmit hook surfaces queued questions/notices on the next prompt.

To listen ACTIVELY (auto-poll without manual wake-up), pair `/khimaira-listen` with `/loop`:

```
/khimaira-listen                # register as listening
/loop 30s /khimaira-poll        # check inbox + incoming every 30s
```

The companion command `/khimaira-poll` runs `session_pending_notes` + `session_incoming_questions` in parallel and processes anything found (answers questions, surfaces notices). When paired with `/loop`, this session becomes responsive to delegation pings on a 30-second cadence without user intervention.

The v2 plan (post-persistent-scheduler / Option 3 in NORTH_STAR follow-up): daemon will push delegation pings directly INTO the listening session via the inbox-note-as-prompt mechanism. At that point `/khimaira-listen` becomes truly passive (no `/loop` needed) — the daemon does the dispatch. Until then, `/loop 30s /khimaira-poll` is the active-listen pattern.

## Steps

1. **Parse `$ARGUMENTS`** — optional human-readable detail text describing what this session is available for (e.g. `"research subagent for jeevy backend"`). If empty, default to `"available for master delegation"`.

2. **Resolve current session id** — from the SessionStart hook context, or `mcp__khimaira__session_list()` fallback. **DO NOT** call `session_set_name` here — naming is `/rename`'s responsibility.

3. **Set listening status**:
   ```python
   mcp__khimaira__session_set_status(
       session_id=<my-id>,
       status="listening",
       detail=<parsed-detail-or-default>,
   )
   ```

4. **Render confirmation**:
   ```
   📡 listening as `<session-name>` (session_id=<8-char-prefix>)
      detail: <parsed-detail>
      master can delegate via `/khimaira-delegate <name> <task>` from its window.

   For ACTIVE polling (auto-respond without manual wake-up):
      /loop 30s /khimaira-poll
   ```

5. **Briefly explain the user contract** (one paragraph):
   - Targeted questions/notices land in this session's inbox.
   - Without `/loop`, you (the user) must type something here to wake the agent.
   - With `/loop 30s /khimaira-poll` running, the agent auto-checks every 30s and processes incoming pings.

## When NOT to use

- **Working on something else in this window**: `listening` status is advisory but if the user calls `/khimaira-delegate <this-name> ...` while you're mid-other-task, the question still lands in your inbox + may interrupt. If you want strict isolation, use a dedicated agent window.
- **End of session**: just close the window. There's no `/khimaira-unlisten` — `session_set_status("idle")` resets if needed, or just `/rename` to a non-listening name.

## Notes

- Listening status is purely informational/advisory. `/khimaira-delegate` doesn't filter by status — it sends to any named target. Status helps Joseph (or future agents calling `session_list`) see which sessions are explicitly available for work.
- The same session can listen AND do other work. `/khimaira-listen` doesn't restrict what else the session does — it just labels it.
- Stop listening: set status back to `idle` via `session_set_status` directly, or use `/khimaira-listen` again with a different status (e.g. just edit your status).
