# /khimaira-spawn-intake [<name>] [reason] — spawn the user-facing intake session

Master-side: request that Joseph spawn a fresh intake session at sonnet/medium, ready to
receive user prompts and translate them into master-delegatable task specs.

**Master must exist before spawning intake.** Intake hands off TO master via chat. If no
master is running, this command fails politely and tells the user to start master first.

The intake role is sonnet/medium, bound to `roles/intake.md`. Intake is the front-end
of the orchestration topology — Joseph talks to it; it translates and routes to master.

```
Joseph → [intake-1] → [master] → [agents × N] + [observers] + [architects on-demand]
```

## Why this exists

The intake pattern fixes the "master is overwhelmed by intent-parsing" failure mode.
When Joseph's requests are fuzzy, ambiguous, or multi-part, master burns Opus cycles
disambiguating before orchestrating. Intake separates those two jobs: intake parses +
clarifies (sonnet/medium is sufficient), then hands master a clean spec to orchestrate
from. Master never sees raw user messages — only the distilled handoff spec.

## Args

```
/khimaira-spawn-intake                    # defaults to intake-1
/khimaira-spawn-intake intake-2           # custom name
/khimaira-spawn-intake intake-v19 "front-end for the v1.9 work session"
```

- **`<name>`** (optional, default: `intake-1`) — kebab-case slug. If a session with this
  name is already active and idle, reuse it.
- **`[reason]`** (optional, everything after the name) — context for the notification.

## Difference from `/khimaira-spawn-architect`

| Dimension | `/khimaira-spawn-architect` | `/khimaira-spawn-intake` (this) |
|---|---|---|
| Audience | master talks to it | Joseph (the user) talks to it |
| Budget | opus/max | sonnet/medium |
| Job | synthesis / design consults | intent parsing + routing to master |
| Invoke primitive | `/khimaira-consult` | direct user conversation |
| Role file | `roles/architect.md` | `roles/intake.md` |

## Steps

1. **Parse `$ARGUMENTS`**:
   - First whitespace token = `<name>` (default `intake-1` if missing)
   - Everything after = `<reason>` (empty string OK)
   - Validate `<name>` matches `^[a-z][a-z0-9-]{0,39}$`

2. **Verify master exists**:
   Call `mcp__khimaira__session_list()`. Check for an active session with
   `status == "orchestrating"` or `status == "idle"` that has `role == "master"` in a
   shared chat. If no master is found:
   ```
   ❌ No active master session found. Intake routes to master — spawn a master first.
   Suggested steps:
     1. Open a new Claude Code window in this project
     2. /rename master (or your preferred name)
     3. /model opus + /effort max
     4. Re-run /khimaira-spawn-intake once master is active
   ```
   Stop.

3. **Check if intake already exists**:
   If a session with `<name>` has `last_active_age_s < 1800` and `status == "idle"` →
   it's ready, skip to step 6.
   If it exists but stale → tell user to refresh it; stop.

4. **Request spawn from Joseph** (intake doesn't exist):

   a. Fire a `PushNotification`:
      ```
      message="Spawn intake: <name> at sonnet/medium — <reason or 'user-facing front-end'>"
      status="proactive"
      ```

   b. Post a notice to every OTHER active session belonging to Joseph:
      ```
      mcp__khimaira__session_post_notice(
          target_session_id=<sid>,
          text=(
              f"🎯 Intake session request from <my-name>: open a new Claude Code window "
              f"in this project (/home/_3ntropy/dev/khimaira), then in that window run:\n"
              f"  /rename <name>\n"
              f"  /model sonnet\n"
              f"  /effort medium\n"
              f"Reason: <reason>. Intake is the user-facing front-end — Joseph talks "
              f"to it, it routes to master via the intake handoff protocol "
              f"(roles/intake.md)."
          ),
          from_session_id=<my-id>,
      )
      ```

   c. **Poll loop**: every 5s for up to 24 iterations (~120s). Each iteration calls
      `session_list()` and checks for `<name>` registered + `last_active_age_s < 60`.

   d. **Timeout** at 120s with no registration:
      ```
      ❌ Intake <name> didn't register within 120s. You can rerun this command, or
         manually spawn the window: /rename <name> + /model sonnet + /effort medium.
      ```
      Stop.

5. **Wake intake with an intro message**:
   ```
   mcp__khimaira__session_post_notice(
       target_session_id=<name>,
       text=(
           "🎯 You are the intake session for <master-name>. Your role (roles/intake.md):\n"
           "  - Joseph talks to YOU — you translate his requests into clean specs.\n"
           "  - When you have a clear spec, send it to master via the intake handoff\n"
           "    protocol: chat_send_to(chat_id, to=[master_id], body=<🎯 INTAKE HANDOFF ...>)\n"
           "  - Ask ONE clarifying question when intent is ambiguous; don't enumerate.\n"
           "  - Don't orchestrate yourself — route to master.\n"
           "  - Stay at sonnet/medium; this is conversation work, not synthesis.\n"
           f"Master is <master-name>. Standby for Joseph's first message."
       ),
       from_session_id=<my-id>,
   )
   ```

6. **Log the registration as a decision**:
   ```
   session_log_decision(
       session_id=<my-id>,
       text="Spawned intake session <name>",
       why=f"Reason: <reason>. Joseph→intake→master topology established."
   )
   ```

7. **Print the user-facing summary**:
   ```
   🎯 Intake <name> ready (sonnet/medium, user-facing front-end).
      Joseph talks to: <name>
      Routes to master: <master-name>

   Intake will translate Joseph's requests into clean specs and hand them to master.
   Master never sees raw user messages — only distilled handoff specs.

   Reason: <reason>
   ```

## When NOT to use

- You want synthesis / architectural depth → use `/khimaira-spawn-architect` instead
- You want master to take a break → use `/khimaira-deputize` (role transfer, not intake)
- No master is running → spawn master first, then intake
- Joseph prefers to talk directly to master (simple session) → skip intake
- The request is already clear and single-step → no intake needed; assign directly

## Notes

- Intake is sonnet/medium — cheap to keep alive between user prompts.
- Intake does NOT need to be invited to every agent chat. Its channel is intake↔master
  (private messages by default once private=True is available).
- The intake-id (8-char hex) is the correlation key for a full user request lifecycle.
  Master includes it in every status update so intake can correlate back.
- Convention: use `intake-1`, `intake-2` for intake sessions.
