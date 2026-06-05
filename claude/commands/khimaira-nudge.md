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

2. **Enumerate windows:** `kitty @ ls` → JSON. For each window collect `{id, title}`.
   Normalize the title: strip leading non-alphanumeric markers (e.g. `✳ `, `* `).

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

4. **Busy check (default ON; skipped with `--busy-too` or a single `<name>`):**
   for each candidate, `kitty @ get-text --match title:<normalized_title> --extent=screen` and read
   the last ~10 lines. If it shows an active spinner, an `esc to interrupt` line, a
   live token/elapsed counter, or an open permission dialog → it's **BUSY**, skip it
   (don't interrupt working agents). Idle windows (empty prompt) are the targets.

5. **Nudge each target window by title** (use `--match title:<normalized_title>`, NOT `--match id:<id>`):
   - `kitty @ send-text --match title:<normalized_title> -- "<NUDGE>"`
   - then submit: `kitty @ send-key --match title:<normalized_title> enter`
   - **Loud-fail**: title-match returns a non-zero exit code when no window with that
     title exists — check the exit code and report FAILED in the table. Do NOT silently
     report "NUDGED" for a failed inject. (By contrast, `--match id:<id>` returns rc=0
     even for dead ids after a restart — a silent no-op that looks like success.)
   - `<NUDGE>` (one line — keep it single-line so `enter` submits it cleanly):
     `⏰ nudge from master: call chat_my_chats(session_id=<your-session-id>) to re-register SSE, then check your inbox + the roster chat. Resume any owed/in-progress task. If you were rate-limited and it has cleared, continue. If genuinely idle with nothing owed, post a one-line standby to the chat. Act now — don't wait.`

6. **Report** a compact table:
   - **NUDGED:** name + window title (one row each).
   - **FAILED:** name + "no window with title <X>" (title-match returned non-zero).
   - **SKIPPED:** name + reason (`master-self` / `busy` / `non-roster` / `wrong-prefix`).
   - End with counts: `nudged N · failed F · skipped M`.

## Notes

- This is real keystroke **injection** — `send-text` + `enter` submits a prompt to
  each window. It only targets roster Claude windows and always skips master + the
  other roster, so it won't hijack your own window or cross rosters.
- **Title-match is stable, id-match is volatile.** Window IDs renumber on every
  restart/resume (`--match id:<stale>` no-ops silently with rc=0 after a restart —
  it looks like success while reaching nothing). `--match title:<name>` uses the
  stable role title and fails loudly (rc != 0) when the window is absent. NEVER
  cache a window id-map across restarts; always re-enumerate `kitty @ ls` fresh.
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
