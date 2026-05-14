# /khimaira-poll — check inbox + incoming questions; process anything found

Companion to `/khimaira-listen`. Pair with `/loop` for active-listening mode:

```
/loop 30s /khimaira-poll
```

Each loop iteration: pull pending notes + incoming questions in parallel, process them, then return. Silent on no-op (so `/loop` doesn't spam the terminal with "nothing pending" lines).

## Steps

1. **Resolve current session id** — from the SessionStart hook context, or `mcp__khimaira__session_list()` fallback.

2. **Pull pending state in parallel** (one batch, two MCP calls):
   - `mcp__khimaira__session_pending_notes(session_id=<my-id>, mark_read=true)` — answers + notices that arrived since last check
   - `mcp__khimaira__session_incoming_questions(session_id=<my-id>)` — open questions other sessions targeted at this one

3. **Process incoming questions** (the load-bearing case for delegation):
   - For each question: read the body, decide if you can answer.
   - If you can answer: do the work + post via `mcp__khimaira__session_post_answer(target_session_id=<asker>, question_id=<qid>, answer=<your answer>, from_session_id=<my-id>)`.
   - If the question needs Joseph's input first (ambiguous, needs codebase access this session doesn't have, etc.): surface to the user — "📨 incoming from <asker>: <question>. I can't answer alone; pausing here." Stop the loop with a brief explanation.

4. **Process notices** (FYI/acks):
   - For each notice: surface compactly.
   - Notices don't need response (per primitive contract).
   - Notes are auto-marked-read by step 2; no further action.

5. **Render output**:
   - **If nothing pending AND no incoming**: print nothing (silent — keeps `/loop` quiet on no-op).
   - **If notices but no questions**: render one line per notice: `📨 from <8-char>: <first 80 chars>`.
   - **If questions answered cleanly**: `✅ answered <N> incoming question(s)`.
   - **If a question needs human input**: render full body + "⏸️ pausing — Joseph, please review."

## When this runs (and when it doesn't)

- **Best paired with `/loop 30s /khimaira-poll`** — interval-based polling. 30s is the recommended cadence: fast enough that delegation feels live, slow enough not to thrash compute.
- **One-shot use is fine** — type `/khimaira-poll` manually to check what's pending right now.
- **Skip during focused work** — don't run inside a complex multi-step task. Save it for between tasks, or run in a dedicated listening window.

## Anti-patterns

- **Don't answer questions without context.** If a question asks "how should we handle X?" and you don't have the project context, surface to the user instead of guessing. Wrong answers are worse than delayed ones.
- **Don't fire `/khimaira-poll` from the master window.** It checks THIS session's inbox — pointless for the session doing the delegating. Run it in the listening agents' windows only.
- **Don't ack notices that look like questions in disguise.** A notice with body "what should I do about X?" is a misuse of `session_post_notice` (questions go through `session_log_question`), but treat the body content as if it were a question: surface + flag the misuse.

## Notes

- Pair with `/khimaira-listen` to set the listening status; `/khimaira-poll` alone doesn't update status (does the work without claiming the role).
- v2 plan (post-persistent-scheduler / Option 3 in NORTH_STAR): the daemon will push incoming pings INTO the session directly, eliminating the need for polling. `/khimaira-poll` becomes vestigial once that ships.
- Silent on no-op is load-bearing — `/loop 30s /khimaira-poll` would be unusable if every iteration printed "nothing pending."
