# /schedule-task <target> <when> <prompt> — daemon-side scheduled wakeup

Schedule a prompt to fire into another session's inbox at a future time. The daemon (`khimaira-monitor`) owns the lifecycle — survives this agent's window closing, retries on failure, observable via `list_scheduled_tasks`.

Use INSTEAD OF `ScheduleWakeup` when the work must survive your current window: cross-session handoffs that need a follow-up, scheduled cron-like maintenance, retries with backoff, fire-and-forget reminders.

Use `ScheduleWakeup` (still the right answer) only for "remind me in 5 minutes within this same conversation."

## Behavior

- Persisted to `~/.local/state/khimaira/scheduled_tasks.jsonl`. Daemon restart does not lose the task.
- **At-least-once** — daemon SIGKILL mid-fire → re-fire on next boot. Prompts MUST be idempotent (check-then-act, upsert, conditional run).
- Fires as a `kind=scheduled-task` note into the target session's inbox. Their UserPromptSubmit hook surfaces it on next user prompt with a `🕒` prefix.
- Target session must be alive at fire time. If not, task retries per `retry_policy` then expires.
- Default TTL 7d. Default retry policy: 1 attempt, 300s linear backoff between retries (opt-in to >1 via `retry_policy`).

## Steps

1. Parse `$ARGUMENTS`:
   - First whitespace-separated token = `<target>` (session name or UUID)
   - Second token = `<when>` — one of:
     - ISO 8601 UTC: `2026-05-15T00:15:00Z` or `2026-05-15T00:15:00+00:00`
     - Relative offset: `+30m`, `+2h`, `+1d`, `+90s`
     - `now` — schedule for immediate fire (mainly for testing)
   - Everything after = `<prompt>` (verbatim text the target agent should run)
   - On malformed args, render:
     ```
     Usage: /schedule-task <target> <when> <prompt>
     Examples:
       /schedule-task khimaira-21 +2h "retry the PyPI publish"
       /schedule-task khimaira-21 2026-05-15T00:15:00Z "run nightly seance reindex"
       /schedule-task my-bot now "ping me, I'm testing this"
     ```

2. Resolve `<when>` to an ISO 8601 UTC timestamp:
   - If it matches `/^[+]\d+[smhd]$/`, compute `now + offset` (in UTC) and emit ISO 8601.
   - If it's `now`, emit current UTC ISO 8601.
   - If it already looks like ISO 8601, pass through (validate it parses).

3. Call `mcp__khimaira__schedule_task(target_session=<target>, fire_at_utc=<iso>, prompt=<prompt>)`. The default retry_policy and expires_in_hours apply unless the user passed `--retries N` or `--expires-h N` flags (parse those before the positional args).

4. Print the response from `schedule_task` verbatim — it includes the task id, fire time, target, and status. The id is what you'd pass to `mcp__khimaira__cancel_scheduled_task` if you needed to revoke before fire.

## When NOT to use

- **Within-conversation timers** (under 30 min, current window stays open) — `ScheduleWakeup` is cheaper and stays in your context.
- **Non-idempotent work** — the scheduler is at-least-once. A double-fire of "send email" or "INSERT" without dedupe will hurt. Either make the prompt idempotent or pick a different primitive.
- **Long-poll waits with no fixed time** — for "fire when X event happens" use a hook or a `/loop` poller, not a scheduled task.

## Notes

- The fired prompt lands as inbox note kind `scheduled-task`. The receiving agent sees it auto-injected on their next user prompt under the standard 📬 khimaira inbox block.
- `list_scheduled_tasks(status="scheduled,pending_retry", target=<name>)` shows what's queued.
- `cancel_scheduled_task(task_id)` revokes — but only valid while status is `scheduled` or `pending_retry`. Mid-fire returns a 409 message; terminal states are idempotent no-ops.
- Cross-session ScheduleWakeup pattern (today): no daemon-side replacement existed, so handoffs cascading wakeups was the workaround. After this command lands, the pattern becomes: schedule once, with `retry_policy={"max_attempts": N, "retry_after_seconds": M}` to handle expected failures (e.g. PyPI throttle → 2h retries).
