# /khimaira-delegate <targets> <task> — fan out a task to N listening agents

Master-side counterpart to `/khimaira-listen`. Sends the same task to N agent sessions in parallel, blocks until they all answer (or timeout), then renders the collected results.

## Args

```
/khimaira-delegate agent-1,agent-2,agent-3 "research how X handles Y; cite file:line"
```

- **targets**: comma-separated list of agent session names or ids. The first whitespace token of `$ARGUMENTS` is the target list. Names resolved via the daemon (UUID or friendly name).
- **task**: everything after the first whitespace — sent verbatim to each agent. Be specific; include the context each agent needs.

## Steps

1. **Parse `$ARGUMENTS`**:
   - Split on first whitespace → `targets_csv`, `task_text`.
   - Split `targets_csv` on commas, strip whitespace → list of target names.
   - If either piece is empty, render usage:
     ```
     Usage: /khimaira-delegate <a1,a2,a3,...> <task description>
     Each agent must have run `/khimaira-listen` first. Default per-target timeout is 15 min.
     ```

2. **Resolve master session id** — from SessionStart hook context or `session_list()` fallback.

3. **Sanity-check targets** (optional but useful):
   - Call `mcp__khimaira__session_list()` once.
   - For each target, warn (don't block) if the named session is missing or has status≠"listening".
   - Surface as `⚠️ agent-2 status=researching (not listening) — sending anyway`.

4. **Fan out** — call `mcp__khimaira__delegate_to_agents` with:
   - `from_session_id=<master-id>`
   - `targets=<parsed list>`
   - `task=<task_text>`
   - `timeout=900` (15 min default; can be overridden if user prefixes `--timeout <N>` before the target list)

5. **Render the result** — the tool returns a JSON dict. For each target, print:
   ```
   ─── agent-1 ───────────────────────────
   <answer body OR ⏱️ timed out / ❌ error message>
   ```
   At the bottom, summarize: "✅ N answered, ⏱️ M timed out, ❌ K errored".

6. **Next-step hint** — based on the results:
   - All answered → suggest the user review + use `/khimaira-accept` or `/khimaira-reject` per agent.
   - Some timed out → suggest user wake those agent windows (type anything) and re-run `/khimaira-delegate` or `/ask <target>`.
   - All errored → flag the daemon may be unreachable; suggest `khimaira monitor start`.

## Caveats to surface

- **Agents must be manually woken.** Each agent's UserPromptSubmit hook only fires when the user types in that window. Until they type, the question sits unread. The slash command should remind the user of this.
- **Per-target timeout** (not aggregate) — one slow agent doesn't block others.
- **Master blocks during the wait.** A 15-min default means the master session is unresponsive for up to 15 min. If you need master to keep working in parallel, the alternative is `mcp__khimaira__session_log_question` (fires + returns immediately; you collect later via `/inbox`).

## Notes

- The fan-out is via one MCP call (`delegate_to_agents`) — not N separate `session_log_question` + `session_wait_for_answer` calls. Cleaner audit trail in the MCP call log.
- This command does NOT auto-write the task results anywhere — they print to the master's window. If you want a record, copy to a tmp file or use `session_log_decision` to capture the outcome.
