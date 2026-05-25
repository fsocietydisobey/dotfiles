# /khimaira-spawn-architect [<name>] [reason] — spawn an architect-role sidecar for synthesis consults

Master-side: request that Joseph spawn a fresh architect sidecar at opus/max, available for
`/khimaira-consult` synthesis questions. **Master stays as master** — no role transfer, no
pause. Distinct from `/khimaira-deputize` which transfers master role and pauses the donor.

The architect role is opus/max, bound to `roles/architect.md`. Spawned sidecars are NOT
auto-invited to chats — invite manually with `chat_invite` if you want them in a multi-agent
chat. Use `/khimaira-consult <name> "<question>"` to consult once spawned.

**Related but different**: `/khimaira-architect` (no spawn) is the chain primitive that writes
IMPLEMENTATION.md design docs via `mcp__khimaira__architect`. This command spawns a live
consult session — same thinking shape, different delivery mechanism.

## Why this exists

The on-demand-architect pattern (banked in master.md): master runs at sonnet/medium for routine
coordination, consults an opus/max architect via `/khimaira-consult` for synthesis/architectural
moments. This command is the setup primitive — it asks Joseph to spawn the architect window,
registers it as consult-ready, and verifies readiness. No master-role transfer.

## Args

```
/khimaira-spawn-architect                    # defaults to architect-1
/khimaira-spawn-architect architect-2        # custom name
/khimaira-spawn-architect arch-v19 "for the v1.9 assign-batch design review"   # name + reason
```

- **`<name>`** (optional, default: `architect-1`) — kebab-case slug. If a session with this
  name is already active and idle, reuse it.
- **`[reason]`** (optional, everything after the name) — context for the PushNotification.

## Difference from `/khimaira-deputize`

| Dimension | `/khimaira-deputize` | `/khimaira-spawn-architect` (this) |
|---|---|---|
| Donor lifecycle | pause — donor flips to `paused`, resumes via `/khimaira-resume` | unchanged — donor stays master |
| Role transfer | Transfers master role across all donor's chats | None — architect starts in no chats |
| Architect purpose | Take over coordination while donor is off-keyboard | Sidecar for synthesis consults via `/khimaira-consult` |
| Resume needed | Yes (`/khimaira-resume` to reclaim master) | No (consult is one-shot per question) |

If you want the architect to TAKE OVER master, use `/khimaira-deputize`. If you want to KEEP
master and have a thinking sidecar, use this command.

## Steps

1. **Parse `$ARGUMENTS`**:
   - First whitespace token = `<name>` (default `architect-1` if missing)
   - Everything after = `<reason>` (empty string OK)
   - Validate `<name>` matches `^[a-z][a-z0-9-]{0,39}$`

2. **Check if the architect already exists**:
   Call `mcp__khimaira__session_list()`. If a session with the matching name has
   `last_active_age_s < 1800` and `status == "idle"` → it's ready, skip to step 6.
   If it exists but `status == "paused"` or stale → tell user to refresh it; stop.

3. **Request spawn from Joseph** (architect doesn't exist):

   a. Fire a single `PushNotification`:
      ```
      message="Spawn architect: <name> at opus/max — <reason or 'consult sidecar'>"
      status="proactive"
      ```

   b. Post a notice to every OTHER active session belonging to Joseph (so it's visible
      wherever he's currently focused):
      ```
      mcp__khimaira__session_post_notice(
          target_session_id=<sid>,
          text=(
              f"🏛️ Architect sidecar request from <my-name>: open a new Claude Code window "
              f"in this project (/home/_3ntropy/dev/khimaira), then in that window run:\n"
              f"  /rename <name>\n"
              f"  /model opus\n"
              f"  /effort max\n"
              f"Reason: <reason>. Master is NOT pausing — architect is a consult sidecar "
              f"bound to roles/architect.md."
          ),
          from_session_id=<my-id>,
      )
      ```

   c. **Poll loop**: every 5s for up to 24 iterations (~120s). Each iteration calls
      `session_list()` and checks for `<name>` registered + `last_active_age_s < 60`.

   d. **Timeout** at 120s with no registration:
      ```
      ❌ Architect <name> didn't register within 120s. You can rerun this command, or
         manually spawn the window: /rename <name> + /model opus + /effort max.
      ```
      Stop.

4. **Wake architect with an intro message** (architect just registered):
   ```
   mcp__khimaira__session_post_notice(
       target_session_id=<name>,
       text=(
           "🏛️ You are an architect sidecar for <master-name>. Your role (roles/architect.md):\n"
           "  - Stay idle until <master> consults you via /khimaira-consult.\n"
           "  - When a 🧠 CONSULT REQUEST arrives in your inbox or chat, think hard\n"
           "    at opus/max and reply via session_post_answer / chat_send.\n"
           "  - DO NOT take initiative on your own — wait for consults.\n"
           "  - Stay at opus/max; do not drop tier.\n"
           "  - Produce one structured synthesis message per consult — not chatter.\n"
           f"Master will fire the first consult shortly. Standby."
       ),
       from_session_id=<my-id>,
   )
   ```

5. **Log the registration as a decision** (for cross-session discoverability):
   ```
   session_log_decision(
       session_id=<my-id>,
       text="Spawned architect sidecar <name>",
       why=f"Reason: <reason>. Available for /khimaira-consult. Donor stays master."
   )
   ```

6. **Print the user-facing summary**:
   ```
   🏛️ Architect <name> ready (opus/max, sidecar mode).
      Master role unchanged (you stay master).
      Consult via: /khimaira-consult <name> "<question>"

   Reason: <reason>
   ```

## When NOT to use

- You want the architect to take over master role → use `/khimaira-deputize` instead
- Master is going off-keyboard for long → use `/khimaira-deputize` (which transfers + pauses)
- You just need a one-shot answer from any session → use `/ask <session> <question>`
- You need a design doc written (IMPLEMENTATION.md) → use `/khimaira-architect` (chain primitive)
- The work is execution, not synthesis → use `/khimaira-assign <agent> <task>`

## Notes

- The architect at opus/max consumes tokens whenever consulted, but is idle (cheap) between
  consults. Multiple consults can run sequentially against the same architect.
- Convention: use `architect-1`, `architect-2`, etc. for sidecar architects. Use specific names
  like `khimaira-0-vice` for handoff deputies (the kind `/khimaira-deputize` uses).
- The architect is NOT auto-invited to any chat. If you want it in a chat for cross-agent
  visibility, invite it manually with `mcp__khimaira-chat__chat_invite` after spawn.
- Consult primitive: `/khimaira-consult <architect> "<question>"` — see that skill for usage.
