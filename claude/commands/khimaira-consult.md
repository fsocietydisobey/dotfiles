# /khimaira-consult <deputy> "<question>" — master consults an opus-tier deputy for a heavy decision

Master-side: send a synthesis/architectural/integration question to a deputy session running at
opus/max, wait for the answer, surface it back in the master window. Lets master stay at
sonnet/medium for routine coordination while still getting opus-grade thinking for the decisions
that need it.

## Args

```
/khimaira-consult deputy-1 "Should we fold _check_stale_acks into the same banner as pending, or keep separate? Trade-offs?"
/khimaira-consult v16-retest-vice "Review the agent-coordination split for the v1.8 work — is the parallel sequencing correct?"
```

- **deputy**: session name (typically the always-on opus session — convention: `deputy-N` or `khimaira-0-vice`)
- **question**: the synthesis/decision/review question — quoted, contains the full context needed

## When to use

Master is at sonnet/medium for routine work but hits a moment that needs opus-grade synthesis:

- **Architectural decisions**: "Should X be folded into Y, or separate?"
- **Complex integration calls**: "How do I wire these N pieces from N agents into one coherent flow?"
- **Design reviews**: "Critique this approach — what am I missing?"
- **Multi-trade-off synthesis**: "Given A, B, C constraints, what's the best path?"
- **Audit calls**: "Did the agents' parallel work actually fit together correctly?"

**NOT for**:
- Routine chat sends / task creates (master handles at sonnet/medium directly)
- Lookups / grep / single-file reads (delegate to a working agent instead)
- Things master can answer in 1-2 sentences without tier escalation
- Tasks that should go to an agent (use `/khimaira-assign` for execution work)

## Steps

1. **Parse `$ARGUMENTS`**:
   - First whitespace-separated token = deputy name
   - Everything after = question text (preserve quotes-as-typed)
   - If either empty: print usage + stop

2. **Resolve master's session id** — from SessionStart context.

3. **Resolve deputy session id** — call `session_list()`, match deputy name. Warn if not found
   or status != "idle" / "listening" — but proceed; consult is best-effort.

4. **Find shared chat** — `chat_my_chats(session_id=<my_id>)`, pick a chat that includes both
   master and deputy. If none, fall back to `session_log_question` (formal Q→A contract).

5. **Send the consult via chat**:
   ```python
   chat_send_to(chat_id, body=<consult_block>, to=[deputy_id])
   ```

   Consult block format:
   ```
   🧠 CONSULT REQUEST [consult-id: <8-char-hex>]
   From: <master session name>
   
   Master is at sonnet/medium for routing — escalating this to you (opus/max) for heavy
   synthesis. Please think hard about it and reply via chat.

   Question:
   <question text>

   Format your reply as:
     💡 CONSULT REPLY [consult-id: <same>]
     <your synthesis>

   Take your time — this is a thinking task. Master will wait.
   ```

6. **Wait for reply** — poll `chat_history(chat_id=<chat_id>, since=<last_event>)` every 15s
   (up to 10 min). Match on `💡 CONSULT REPLY [consult-id: <id>]` from the deputy.

7. **Surface the reply in master window** verbatim:
   ```
   🧠 Deputy <name> (opus/max) consulted on: <question first line>

   <reply body>

   ─── proceed with this synthesis or push back if you disagree ───
   ```

8. **Timeout path**: if no reply in 10 min, print:
   ```
   ⏱️ Deputy <name> didn't respond within 10 min. Options:
     - Wake the deputy window (type anything in it) and re-run /khimaira-consult
     - Self-escalate: type `/model opus` `/effort max` in this window and think it through
     - Skip the consult and decide at current tier
   ```

## Notes

- The consult pattern is intentionally synchronous from master's perspective (block + wait).
  Master shouldn't be doing other work while a critical synthesis is pending.
- Deputy at opus/max should HAVE been spawned via `/khimaira-deputize` earlier in the session,
  or set up at the start of the work pattern.
- Multiple consults can run sequentially against the same deputy (different consult-ids).
- The deputy's reply IS the synthesis — master takes it at face value and proceeds. If master
  disagrees, that's its own decision to push back or re-consult.
- Cost reasoning: 1 opus turn (the consult) << N opus turns (master at opus the whole time).
  The consult is cheap because the deputy returns to idle after replying.

## See also

- `/khimaira-deputize <vice-name>` — spawn / promote a deputy session
- `/khimaira-assign <agent> <task>` — delegate executable work (different shape: execution, not synthesis)
- `/ask <session> <question>` — synchronous cross-session ask (lighter-weight, same wire pattern)
