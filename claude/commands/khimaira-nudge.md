# /khimaira-nudge [name | --prefix P] [--busy-too] — wake idle/stuck/rate-limited roster agents

Manual keystroke-wake for roster agent windows that have gone idle, silent, or
stuck (including rate-limit recovery) — the manual counterpart to the daemon's
auto-wake (`roster_recovery`'s `send-text` path). Injects a re-orient prompt into
each agent's kitty window so it re-registers SSE, checks its inbox + the roster
chat, and resumes any owed task.

**Use when:** agents are sitting idle, the auto-wake isn't catching them, a
rate-limit window just cleared, or you posted something (a notice/answer) and the
target session is idle so it hasn't surfaced yet (notices are turn-gated — a nudge
forces the turn).

## Args

- **(none)** — nudge ALL khimaira-roster worker windows (excludes master + the jp roster).
- **`<name>`** — nudge only the named window (e.g. `agent-3`, `frontend-lead-1`, `janice-0`).
- **`--prefix <p>`** — target a prefixed roster instead (e.g. `--prefix jp` for `jp-*` windows).
- **`--busy-too`** — also nudge windows that look busy (default: skip busy windows so working agents aren't interrupted).

## Steps

1. **Require kitty remote control.** Verify `kitty @ ls` works (run inside kitty
   with `allow_remote_control yes`). If it fails, tell the user to enable remote
   control in `kitty.conf` and stop.

2. **Enumerate windows:** `kitty @ ls` → JSON. For each window collect `{id, title}`
   — **keep the `id` paired with every title; it is the actuation handle (steps 4–5),
   not just metadata.** Normalize the title for MATCHING by stripping kitty's dynamic
   decoration markers (e.g. `✳ ` activity, `⠂`/braille thinking-spinner, `* ` bell).
   These markers are LIVE and flicker with session state, so they must never be part
   of the string you match on — match the normalized name, actuate by the paired id.

3. **Select targets** (build the list; print it before nudging):
   - **Default (no `--prefix`):** normalized titles matching khimaira-roster worker
     roles — `agent-\d+`, `(backend|data|frontend)-lead-\d+`, `architect-\d+`,
     `analyst-\d+`, `critic-\d+`, `verifier-\d+`, `observer-\d+`, `intake-\d+`,
     `tracker-\d+`. **EXCLUDE** master (`khimaira-0`, `*-0`, the window you're running
     in) — never nudge yourself. **EXCLUDE** any `jp-*` title (the other roster).
   - **`--prefix <p>`:** only titles starting with `<p>-`, same role patterns, and
     exclude that roster's master (`<p>-master-*`; for jp, also `janice-0`).
   - **`<name>` arg:** exactly that one window (normalized-title match). A bare name
     bypasses the busy-skip (an explicit single target is deliberate).

   ⚠️ **Cross-roster safety lives in the SELECTION FILTER, not in a kitty match string.**
   The role-pattern + roster-exclusion above (`muther-*`/`jp-*` excluded, `^<role>-N>`
   shape required) is what keeps you from cross-firing a sister roster's twin window.
   On 2026-06-07 an unanchored `title:agent-1` substring-matched all 12 `muther-agent-1…`
   windows. The fix is NOT "anchor the kitty title match" (that races the dynamic marker
   — see below) — it's "decide the target set in-agent from the enumerated `{id, title}`
   list, then actuate each chosen window BY ITS id."

4. **Busy check (default ON; skipped with `--busy-too` or a single `<name>`):**
   for each selected candidate, `kitty @ get-text --match id:<id> --extent=screen`
   (use the paired id from step 2 — NOT a title-match) and read the last ~10 lines. If
   it shows an active spinner, an `esc to interrupt` line, a live token/elapsed counter,
   or an open permission dialog → it's **BUSY**, skip it (don't interrupt working agents).
   Idle windows (empty prompt) are the targets.

5. **Nudge each target window BY ITS id** (the id paired with the title in step 2 — a
   FRESH id from this invocation's `kitty @ ls`, so the "stale id" hazard does not apply):
   - `kitty @ send-text --match id:<id> -- "<NUDGE>"`
   - **Readback-verify (loud-fail):** `kitty @ get-text --match id:<id> --extent=screen`
     and confirm the `<NUDGE>` text (or a unique token from it) is present in the buffer.
     If it is NOT, the inject did not land — `kitty @ send-key --match id:<id> ctrl+c`
     to clear and report **FAILED** for that window. Do NOT report "NUDGED" without this
     readback confirmation. (This is why we don't rely on exit codes: a kitty match that
     resolves zero windows still returns rc=0 — a SILENT no-op. The readback is the only
     trustworthy success signal. The daemon's auto-wake uses the same nonce-readback guard.)
   - On confirmed landing, submit: `kitty @ send-key --match id:<id> enter`
   - `<NUDGE>` (one line — keep it single-line so `enter` submits it cleanly):
     `⏰ nudge from master: call chat_my_chats(session_id=<your-session-id>) to re-register SSE, then check your inbox + the roster chat. Resume any owed/in-progress task. If you were rate-limited and it has cleared, continue. If genuinely idle with nothing owed, post a one-line standby to the chat. Act now — don't wait.`

6. **Report** a compact table:
   - **NUDGED:** name + window title (one row each) — only after readback confirmed landing.
   - **FAILED:** name + reason (`inject not in buffer after readback` / `id <X> gone from ls`).
   - **SKIPPED:** name + reason (`master-self` / `busy` / `non-roster` / `wrong-prefix`).
   - End with counts: `nudged N · failed F · skipped M`.

## Notes

- This is real keystroke **injection** — `send-text` + `enter` submits a prompt to
  each window. It only targets roster Claude windows and always skips master + the
  other roster, so it won't hijack your own window or cross rosters.
- **Select by title, actuate by FRESH id, confirm by readback.** The earlier guidance
  ("title-match is stable, id-match is volatile") was half-right and caused a real bug
  (2026-06-20): kitty decorates live window titles with DYNAMIC markers (`✳ ` activity,
  `⠂`/braille thinking-spinner, `* ` bell) that an anchored `title:^name$` cannot match —
  so the title-match silently no-ops (rc=0, keystrokes go nowhere) AND the marker can
  flicker between the busy-check and the nudge. The daemon's auto-wake hit this exact
  failure on the `✳ livyatan` window. The volatile-id hazard is REAL but only across
  RESTARTS — an id read from THIS invocation's `kitty @ ls` is fresh, not cached, so it's
  safe. Resolution: never cache an id-map across restarts (always re-enumerate fresh),
  match the normalized name in-agent to pick targets, actuate by the paired fresh id, and
  treat the post-inject readback (not an exit code) as the only trustworthy success signal.
- A **still-rate-limited** window won't act (it's capped) — the nudge submits but the
  agent can't respond until the cap resets. Re-run after a few minutes; the nudge is
  idempotent.
- Default **skips busy windows** so you don't interrupt an agent mid-edit. Pass
  `--busy-too` to force-nudge everyone (use deliberately, e.g. a full-roster reset).
- Pairs with the daemon's auto-wake; this is the manual escape hatch when the
  auto-path isn't catching idle/stuck agents (and when a turn-gated notice/answer is
  sitting unseen in an idle session's inbox — the nudge forces the turn that surfaces it).
- **Cross-roster:** to nudge the jp roster from here, `--prefix jp`. To nudge a single
  idle session that's holding an unsurfaced notice (e.g. `janice-0`), `/khimaira-nudge janice-0`.
