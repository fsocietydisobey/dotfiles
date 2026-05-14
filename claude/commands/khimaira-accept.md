# /khimaira-accept <targets> [feedback] — master confirms agent results

After `/khimaira-delegate` returns, master inspects each agent's answer and decides. `/khimaira-accept` is the positive-ack path: the work is good, no rework needed, just close the loop with the agent so they know.

## Args

```
/khimaira-accept agent-1,agent-3 "good citations, merging"
/khimaira-accept agent-2
```

- **targets**: comma-separated list of agents to acknowledge.
- **feedback**: optional. Defaults to "accepted — work integrated."

## Steps

1. **Parse `$ARGUMENTS`** — first whitespace token is the comma-separated targets; everything after is the optional feedback.

2. **Resolve master session id**.

3. **For each target**, call `mcp__khimaira__session_post_notice` with:
   - `target_session_id=<agent>`
   - `text="✅ master accepted your work. <feedback>"`
   - `from_session_id=<master>`

4. **Render**:
   ```
   ✅ accepted: agent-1, agent-3
   ```

## When this matters vs. silent-master

- If you don't `/khimaira-accept`, the agent has no way to know whether their work was used. For multi-round work blocks, that breeds the "did master ever see my answer?" question.
- This is FYI-only — it doesn't gate anything, doesn't trigger any state change on the agent's side. Just closes the human-readable loop.

## Notes

- This command does NOT modify any code, push anything, or change any state beyond posting a notice to each agent's inbox.
- To reject + give rework context, use `/khimaira-reject` instead.
