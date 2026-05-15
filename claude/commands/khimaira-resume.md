# /khimaira-resume — restore master role across deputized chats

Resume orchestration after a `/khimaira-deputize` handoff. Reads `room.meta.deputized_original_master` on each chat the caller donated; atomically swaps master role back via the daemon's `chat_resume_master` primitive. No vice cooperation required — admin-style restoration symmetric to v2's `chat_set_creator` for orphaned-master unlock.

## Why this exists

When `/khimaira-deputize` hands master role to a vice session, the donor's status flips to `paused`. The vice drives orchestration (review outlines, approve done tasks, can spawn its own sub-tasks). When the donor returns to their keyboard, they need to reclaim master role across the chats they donated.

`/khimaira-resume` closes the loop. It composes:

- `find_chats_deputized_by(me)` — daemon-side helper that scans chat META for the deputize marker.
- `chat_resume_master(chat_id, me)` — admin primitive gated on `meta.deputized_original_master == me`; atomically demotes current master (the vice) back to agent and promotes the caller back to master; clears the marker; emits v1.5 role directives to both sides.
- Donor status flip back to `orchestrating` (parsing the `pre:` token stashed in the paused detail by `/khimaira-deputize` to restore prior context).
- `session_post_notice` to each vice thanking them for the watch.

Per Phase B v1.6 spec (`tasks/khimaira-chat/PHASE-B-V1.6-VICE.md`) + LOCK v2 (chat-400516f81475 msg-9940389c03b5): the chat-meta marker is the single source of truth; the primitive doesn't require vice cooperation.

## Args

None. Reads donor's own session state + chat META.

## Steps

1. **Resolve own session id** — from SessionStart hook context. Call this `me`.

2. **Pre-flight: verify `paused` status.** Call `mcp__khimaira__session_state(me)`. If status is not `paused`, render:
   ```
   ⚠️ Not currently deputized. /khimaira-resume only works when status is "paused"
   (i.e., after a /khimaira-deputize call). Current status: <actual-status>.
   ```
   and STOP.

3. **Parse the `pre:` token from paused detail.** The deputize skill stashes prior status detail via the convention `paused | pre: "<prior-detail>" | deputized to <vice-name>` in the donor's `status_detail`. Extract:
   - `<prior-detail>` substring between `pre: "` and `"`.
   - `<vice-name>` substring after `deputized to `.

   If the `pre:` token is absent (donor was deputized via a path that didn't stash), `<prior-detail>` is None — fall back to a generic restore-string in step 7.

4. **Enumerate deputized chats** — call the daemon's `find_chats_deputized_by(me)` helper. Returns a list of chat_ids where `me` is the recorded `deputized_original_master`. Possibly empty (e.g., user manually cleared a chat's marker, or the deputize timed out before transferring) — render an informational message and continue with status restore.

5. **Resume each chat** — for each chat_id from step 4:
   - Call `chat_resume_master(chat_id, me)`. Daemon atomically:
     - Demotes current master (vice) → agent in `member_roles`.
     - Promotes `me` → master in `member_roles`.
     - Restores `created_by = me` and `created_by_name = me's name`.
     - Clears `meta.deputized_original_master`.
     - Emits v1.5 role directives: `me` → master (with /model + /effort suggestion), vice → agent.
   - On per-chat failure (e.g., chat archived between deputize and resume): log + continue. Don't roll back successful resumes.
   - Collect `resumed`, `failed` lists.

6. **Notice the vice(s)** — for each unique vice session across resumed chats:
   - `mcp__khimaira__session_post_notice(target_session_id=<vice-sid>, text="🪪 Resume notice from <me>: I've taken master back across <N> chat(s). Thanks for the watch. Your role in those chats is now `agent` — see the 🎚️ role directives in each chat for the demoted budget recommendation.", from=<me>)`.

7. **Restore status** — `mcp__khimaira__session_set_status(me, status="orchestrating", detail=<restore-detail>)`. Build `<restore-detail>`:
   - If `<prior-detail>` was successfully parsed in step 3: use it verbatim. Restores the donor's pre-deputize working context.
   - If not (no `pre:` token or parse failure): fall back to `"resumed from deputization to <vice-name>"`.

8. **Print user summary** to Joseph:
   ```
   🪪 Resumed master across <N> chats: [<chat_id_1>, <chat_id_2>, ...]
   Failed: [<chat_id>, ...] (or "none")
   Status restored: "<restore-detail>"
   ```

## Token-parse template (for step 3)

The deputize skill writes the paused detail as:
```
paused | pre: "<prior-detail>" | deputized to <vice-name>
```

Parse with a single regex (or simple `.find`-based split). Defensive notes:
- `<prior-detail>` may contain quotes — match non-greedy between `pre: "` and the LAST `" | deputized to` occurrence.
- `<vice-name>` is everything after the FINAL ` | deputized to ` (kebab-case slug, no spaces).
- If parse fails, treat as no-stash and fall through to the generic restore-string.

## Notes

- **Chained deputize gap** (LOCK v2 Decision 6, deferred to v1.7): if the vice deputized to a vice-vice during the donor's pause, `chat_resume_master` correctly demotes the vice-vice (the current master) and restores the donor — but the middle vice's session-state stays `paused`. Surface a hint in the user summary if this is detectable (`member_roles[<original-vice>] != ROLE_AGENT` post-resume implies they were further-deputized; manual cleanup may be needed on the middle session).

- **Vice cooperation not required**. Unlike the paired-slash-command alternative (option a from the spec's Open Q §1), `chat_resume_master` is daemon-side gated on the chat-meta marker. The vice doesn't need to be online or responsive for the donor to reclaim — symmetric to v2's `chat_set_creator` orphan-unlock. This is load-bearing for real failure modes (vice off-keyboard, vice mid-deep-research, vice context-cleared).

- **Idempotent retry**. If a per-chat resume failed in step 5, rerunning `/khimaira-resume` will retry only chats still marked as deputized (the marker on successfully-resumed chats is cleared). No special "force resume all" flag needed.

- **What if I'm not the original master?** `chat_resume_master` raises `ValueError` with "not the original master" if the caller doesn't match `meta.deputized_original_master`. This shouldn't happen in normal flow (the slash command is keyed off the caller's own paused-state), but defends against edge cases like a third party trying to forcibly claim master role.

## Distinction from `/khimaira-deputize`

| Dimension | `/khimaira-deputize` | `/khimaira-resume` |
|---|---|---|
| Donor lifecycle | active → paused | paused → orchestrating |
| Direction | grant master to vice | reclaim master from vice |
| Spawning | requests spawn if vice doesn't exist | no spawn — vice already exists |
| Authority check | caller must be current master | caller must be `meta.deputized_original_master` |
| Composes from | `chat_transfer_membership(..., as_deputize=True)` | `chat_resume_master` + `find_chats_deputized_by` |

The two skills are inverses; running `/khimaira-deputize <vice>` then `/khimaira-resume` restores the chat to its pre-deputize state (modulo any work the vice did in between, which is preserved in the JSONL).
