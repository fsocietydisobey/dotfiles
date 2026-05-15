# /khimaira-deputize <vice-name> [reason] — pause-and-handoff master role to a fresh vice

Spawn (or reuse) a vice session, transfer your master role across all your chats, and flip your own status to `paused`. Resume later via `/khimaira-resume` — the donor stays alive (not transferred-out) and reclaims master when ready.

## Why this exists

Master-as-bottleneck mitigation: master is reviewing + answering Joseph + drafting, and lane workers stall on greenlights. Per `tasks/khimaira-chat/PHASE-B-V1.6-VICE.md`, this is an application gap with a correctness sub-invariant — recommendation primitive (this command + `/khimaira-resume`) layered over enforcement primitive (`chat_resume_master`, Phase B v1.6 L2). Distinct from `/khimaira-transfer-session`: that's terminal; this is pause-and-handoff (donor stays alive, reclaims master via `/khimaira-resume`).

## Args

```
/khimaira-deputize <vice-name> [reason...]
```

- **`<vice-name>`** (required) — kebab-case slug for the new vice session (e.g. `khimaira-0-vice`, `master-deputy-1`). If a session with this name is already active, that session is the target; otherwise we request Joseph spawn one.
- **`[reason]`** (optional, everything after the vice-name) — free-form context surfaced in the user-facing PushNotification + vice brief. Examples: `"answering Joseph's question, expect 5-10min"`, `"deep research on X, off-keyboard 30min"`.

If `<vice-name>` is empty, render usage and stop.

## Steps for the donor (this session)

### 1. Parse `$ARGUMENTS`

First whitespace token = `<vice-name>`. Everything after = `<reason>` (empty string if omitted). Validate `<vice-name>` matches `^[a-z][a-z0-9-]{0,39}$`; otherwise render usage and stop.

### 2. Pre-flight checks

Resolve your own session id (from the SessionStart hook). Call `mcp__khimaira__session_state(session_id=<my-id>, recent=5)`. If `status` is already `paused` or `transferred-out`, reject:

```
❌ This session is already <status>. Resume via /khimaira-resume first, then re-deputize if needed.
```

**Capture the current `status` + `status_detail`** — you'll embed the prior detail in the new paused status per the pre-pause-detail-stash convention (see Notes).

### 3. Check if the vice already exists

Call `mcp__khimaira__session_list()`. If a session named `<vice-name>` has `last_active_age_s` under ~1800s (~30 min), it's live — skip to step 5 with that session as the target.

If absent or stale, proceed to step 4 (request spawn).

### 4. Request spawn from Joseph

This is the load-bearing chicken-and-egg fix: the master can't spawn a Claude Code window itself.

a. Fire one PushNotification:
   ```
   PushNotification(
       message="<my-name> requesting deputy: <vice-name> — <reason or 'pause-and-handoff'>",
       status="proactive",
   )
   ```
   Keep under 200 chars; lead with the vice-name + a short hint.

b. Post a notice to every other active session belonging to Joseph (so the request is visible in whichever window he's currently in). Loop the `session_list()` result, filter to sessions with `last_active_age_s` < 1800 AND `session_id != my-id` AND `name != <vice-name>`, and for each:
   ```
   mcp__khimaira__session_post_notice(
       target_session_id=<sid>,
       text=(
           f"🪪 Deputize request from <my-name>: open a new Claude Code window "
           f"in this project, then run `session_set_name(name='<vice-name>')`. "
           f"Reason: <reason>. Master is paused until vice registers."
       ),
       from_session_id=<my-id>,
   )
   ```

c. **Poll loop**: every 5s for up to 24 iterations (~120s total). Each iteration calls `session_list()` and checks for `<vice-name>` registered + `last_active_age_s` < 60. Shape (Bash inside the agent's runtime):
   ```bash
   for i in {1..24}; do
     # call session_list, parse for <vice-name> active
     if found; then break; fi
     sleep 5
   done
   ```
   Implement via repeated `session_list` calls + a check; sleep between calls.

d. **Timeout**: if 120s elapses with no vice registration, print:
   ```
   ❌ Deputization request timed out after 120s — vice <vice-name> never spawned.
      Joseph can rerun /khimaira-deputize <vice-name> [reason] to retry.
   ```
   **Do NOT flip donor status; do NOT transfer anything.** Stop.

### 5. Enumerate chats where you hold master + transfer each

Call `mcp__khimaira-chat__chat_my_chats(session_id=<my-id>)` → list of accepted chats. For each chat:

- Read `room.meta` (via `mcp__khimaira-chat__chat_history` or equivalent) to determine if you hold master via `member_roles[<my-id>] == "master"` OR the v1 fallback `created_by == <my-id>` when `member_roles` is absent.
- **Skip chats where you're a regular member but not master** — collect into a `skipped` list for the user summary.
- **For each master chat**, call:
  ```
  mcp__khimaira-chat__chat_transfer_membership(
      chat_id=<id>,
      from_session_id=<my-id>,
      to_session_id=<vice-name>,
      as_deputize=True,
  )
  ```
  The `as_deputize=True` kwarg (Phase B v1.6 L2) sets `room.meta.deputized_original_master = <my-id>` atomically with the master-role swap. Phase B v1.5's role-directive emit fires automatically — the vice sees `🎚️ Role updated: you are now master. /model opus, /effort max.` in each chat.
- Continue on per-chat failure (don't roll back successes); collect into a `failed` list.

### 6. Flip donor status + log the deputization decision

Compose paused detail per the **pre-pause-detail-stash convention**: `paused | pre: "<captured prior detail from step 2>" | deputized to <vice-name>` (see Notes).

Call `mcp__khimaira__session_set_status(session_id=<my-id>, status="paused", detail=<composed>)` then `mcp__khimaira__session_log_decision(session_id=<my-id>, text="Deputized to <vice>; transferred N chats", why="Reason: <reason>. Chats: [<chat_id1>, ...]. Vice inherits master + v1.5 budget directive. Resume via /khimaira-resume.")`.

### 7. Brief the vice + print user-facing summary

Compose the vice brief (template below); post via `session_post_notice(target=<vice-name>, text=<brief>, from=<my-id>)`. Then print to Joseph:

```
🪪 Deputized to <vice-name>.
   Transferred: <N> chats — [chat-xxxx, ...]
   Skipped (non-master): <M> chats — [chat-zzzz, ...]
   Failed: <F> chats — [(chat_id, error)]
Resume via /khimaira-resume when ready.
```

## Vice-brief template

Fill bracketed sections from gathered data (per-chat `chat_task_status` for the mid-flight list); pass as `text` to `session_post_notice`:

```
🪪 DEPUTIZATION BRIEF — you are now master of <N> chats.
Reason donor paused: <reason>

Chats transferred (v1.5 directive already landed in each):
- chat-xxxx — "<title>" — <K> tasks (<pending=A, in_progress=B, done=C>)
- chat-yyyy — ...

Priorities (donor's read): <optional line, e.g. "L1 outline awaiting greenlight">

Hand back: when donor types /khimaira-resume they regain master + you demote to agent.
```

## Distinction from `/khimaira-transfer-session`

The two commands look similar but have different lifecycles:

| Dimension | `/khimaira-transfer-session` | `/khimaira-deputize` |
|---|---|---|
| Donor lifecycle | terminal — donor becomes `transferred-out` | pause — donor stays alive (`paused`), returns via `/khimaira-resume` |
| Duration | 24h TTL on the handoff | open-ended; Joseph drives resume |
| Scope | git project root | per-session (all donor's master chats) |
| Spawning | Joseph spawns recipient first | this command requests spawn if vice doesn't exist |
| Chat meta marker | none | `room.meta.deputized_original_master = donor_sid` |

## Notes

- **Pre-pause-detail-stash convention** (LOCK v2 Decision 4): paused `detail` carries the donor's prior detail in a parseable format — `paused | pre: "<prior-detail>" | deputized to <vice>`. Convention not schema; `/khimaira-resume` parses + restores, falls back to generic if absent.
- **Chained deputization unsupported in v1.6** — if vice further deputizes to a vice-vice, `/khimaira-resume` correctly restores master on this donor's chats but won't auto-clean the intermediate vice's `paused` state. v1.7+ may add multi-level support.
- **When NOT to use**: terminal handoffs (context window full, off-keyboard for days) → `/khimaira-transfer-session`. Deputize is for short-to-medium pauses where donor reclaims master.
- **Vice cooperation NOT required for resume** (Phase B v1.6 L2): `chat_resume_master` is admin-style; donor reclaims unilaterally. Vice's `chat_send` continues during deputization; vice loses only master gating on resume.
