# /khimaira-write-handoff — capture current roster state as a handoff for the next session

Call this before killing a roster or when context bloat is forcing a restart.
Generates a structured handoff from live session state and posts it to the
khimaira handoff queue so the next master session auto-loads it at first turn.

## Steps

1. **Resolve session_id** from the `🆔 khimaira session_id` block.

2. **Gather state** by running these in parallel:
   - `mcp__khimaira__session_recent_decisions(session_id=<id>, limit=20)` — what was decided
   - `mcp__khimaira__session_list()` — which sessions are active, their names/roles
   - Check `chat_history(chat_id=<active_roster_chat>, limit=10)` for recent done-reports / pending gates
   - Check mnemosyne domains: `curl -sf http://127.0.0.1:8766/domains`

3. **Build the handoff text** — structured as:

```
HANDOFF from <session_name> (<session_id[:8]>, <date>)

═══ FIRST STEPS ═══
[Most important action for the next master — join roster chat, approve pending tasks, etc.]

═══ PENDING (need attention) ═══
[Tasks with gates cleared but not yet committed/approved]
[Open blockers agents are waiting on]

═══ ACTIVE ROSTER ═══
[chat_id and title of the active roster chat]
[Which agents are mid-task]

═══ RECENT DECISIONS ═══
[Top 5-10 decisions from session_recent_decisions, condensed]

═══ OPEN BACKLOG ═══
[Numbered list of pending tasks by priority]

═══ KEY CONTEXT ═══
[Anything non-obvious the next session needs: active workarounds, known bugs, architectural choices made this session]
```

4. **Post the handoff:**
```python
mcp__khimaira__session_post_handoff(
    from_session_id="<session_id>",
    text="<handoff text>",
    scope_cwd="<cwd>"  # e.g. /home/_3ntropy/dev/khimaira
)
```

5. **Distill into mnemosyne** (if mnemosyne is running at port 8766):
   For each relevant domain (orchestration, architecture, etc.) — run a distill call
   with the key decisions from this session as transcript. Use direct HTTP if the
   mnemosyne_client returns None:
   ```bash
   curl -sf -X POST http://127.0.0.1:8766/distill \
     -H 'Content-Type: application/json' \
     -d '{"domain":"khimaira:orchestration","session_slug":"<name>","transcript":"<key learnings>"}'
   ```

6. **Report** — print the handoff id, mnemosyne pairs extracted per domain,
   and confirm: "Handoff posted. Next master will see this at first turn."

## Notes

- Keep the handoff under ~2000 tokens — the next session reads it as additionalContext
- Prioritize: what does the next master need to DO, not a full history
- The `session_post_handoff` call scopes to `cwd` so only sessions in this project claim it
- Mnemosyne may be down (it's a separate process); distill is best-effort, skip if unavailable
- This command replaces the need to manually call `/handoffs` at session start — the next master's UserPromptSubmit hook will inject this handoff automatically on the first turn
