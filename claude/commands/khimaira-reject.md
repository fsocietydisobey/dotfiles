# /khimaira-reject <targets> <rework-context> — master sends an agent back for rework

After `/khimaira-delegate` returns, if an agent's answer wasn't right (wrong file, missed context, incorrect citation, etc.), master uses `/khimaira-reject` to send the agent a NEW targeted question with rework context. The agent then answers the new question; master can `/khimaira-delegate` again or just `session_wait_for_answer`.

## Args

```
/khimaira-reject agent-2 "missed the auth/ feature — focus there, ignore everything else"
/khimaira-reject agent-1,agent-4 "wrong codebase, you're in jeevy_portal not khimaira"
```

- **targets**: comma-separated list of agents to send back.
- **rework-context**: required — everything after the targets. Without rework context the agent has no signal for what to do differently.

## Steps

1. **Parse `$ARGUMENTS`** — first whitespace token is targets; everything after is rework context.

2. **Validate** — if no rework context after the targets, render:
   ```
   Usage: /khimaira-reject <agent1,agent2,...> <rework-context>
   Rework context is required — without it the agent can't tell what to fix.
   ```

3. **Resolve master session id**.

4. **For each target**, call `mcp__khimaira__session_log_question` with:
   - `session_id=<master>`
   - `target_session_id=<agent>`
   - `text=`
     ```
     ❌ master rejected your previous answer. Rework context:
     <rework-context>
     
     Please retry the original task with this in mind. Use the same
     output format you used before.
     ```

5. **Render**:
   ```
   🔁 reworking with agent-2, agent-4
   Each agent's hook will surface the new question on its next turn.
   Wake each window (type anything) and they'll see the rework ask.
   You can `session_wait_for_answer` on the new question ids OR re-run
   `/khimaira-delegate` to fan them out alongside other work.
   ```

## Caveats

- This creates a NEW question per target. The original answered question stays in the archive; you can refer back to it via `/inbox <agent>` or `session_query_transcript`.
- Master does NOT block here — `/khimaira-reject` fires the questions and returns. Use `/khimaira-delegate` if you want to await the new answers, or `session_wait_for_answer` on the new question ids returned by this command.
- Don't `/khimaira-reject` without rework context — agents have no way to infer what to change. Vague reject = vague rework.

## Notes

- The rework context is sent verbatim. If the original task was long + context-heavy, the rework ask doesn't need to repeat it (the agent has the prior question + your answer in its session_state already). Just say what was wrong + what to do.
