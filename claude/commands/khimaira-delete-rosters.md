# /khimaira-delete-rosters [--prefix P] [--dry-run] — delete PREVIOUS rosters, keep the current

Clean up orphaned / previous-roster sessions so `session_list` and the Claude Code
resume picker aren't cluttered by stale rosters. Deletes all sessions of a roster
PREFIX that are **not** part of the currently-active roster.

**SAFE BY CONSTRUCTION.** This command leans on `delete_session`'s alive-guard
(`KHIMAIRA_ALIVE_DELETE_GUARD_S`, default 900s, fix d7b4eb7): a currently-active
session is **refused** at the daemon, so the live roster can never be orphaned —
even if a name resolves to a live session. The command targets prefix-matching
sessions; the guard skips the ones still running.

## Why this exists

Ad-hoc roster deletion (delete by name) resolves a name to the most-recently-active
session — which is the LIVE one — and `delete_session` leaves it from every chat
(`state='left'`, which cannot self-rejoin). That silently orphaned the running
roster (the recurring re-invite churn). This command + the alive-guard make roster
cleanup safe: it targets the prefix's sessions and the guard protects the active ones.

## Args

- **(none)** — the un-prefixed khimaira roster (roles: `agent-N`, `architect-N`,
  `analyst-N`, `critic-N`, `verifier-N`, `observer-N`, `intake-N`, `tracker-N`,
  `(backend|data|frontend)-lead-N`, `khimaira-N`). EXCLUDES any `jp-*` (the other roster).
- **`--prefix <p>`** — a prefixed roster (e.g. `--prefix jp` → only `jp-*`). NEVER
  cross-deletes the other roster.
- **`--dry-run`** — list what WOULD be deleted; delete nothing.

## Steps

1. **Resolve the current master session id** (this session). Never delete self.
2. `mcp__khimaira__session_list()` — all sessions (name + id + last_active_age_s).
3. **Build the target set** — sessions whose name matches the roster role-pattern for
   the prefix:
   - **no prefix:** name matches `^(agent|architect|analyst|critic|verifier|observer|intake|tracker)-\d+$`
     or `^(backend|data|frontend)-lead-\d+$` or `^khimaira-\d+$`. EXCLUDE any name
     starting `jp-`. EXCLUDE the current master (`khimaira-0` / self).
   - **`--prefix p`:** name starts `p-`, same role suffixes. EXCLUDE that roster's
     master (`p-master-*`; for jp also `janice-0`).
4. **For each target session_id**, call
   `mcp__khimaira__session_delete(session_id=<exact-uuid>, force=true)`.
   ALWAYS pass the **exact UUID** from `session_list`, never an 8-char prefix or a
   friendly name (name-collision is the original bug — `4ce4` vs `4ec4`).
   - Result `{"active": true, ...}` → the alive-guard refused it: this is the CURRENT
     roster, correctly protected. Count as **KEPT**.
   - Result `{"deleted": true, ...}` → a stale previous-roster session. Count as **DELETED**.
   - Result `{"error": ...}` (not-found / etc.) → count as **SKIPPED** with the reason.
   - With `--dry-run`: don't call delete; just classify by `last_active_age_s`
     (≥900s = would-delete, <900s = would-keep-active).
5. **Report** a compact table:
   - **DELETED:** name + 8-char id + age (previous rosters).
   - **KEPT (active):** name + id (current roster — guard-protected).
   - **SKIPPED:** name + reason.
   - End: `deleted N · kept M active · skipped K`.

## Notes

- **The alive-guard is the real safety** — this command cannot orphan the live roster
  because active sessions are refused at `delete_session`. The prefix/role filtering is
  the targeting; the guard is the protection.
- `delete_session` also leaves the session's chats (`state='left'`) and archives its
  decisions (force) — correct for a genuinely previous (dead) roster session.
- **Prefix isolation:** `--prefix jp` only touches `jp-*`; the bare form only touches
  un-prefixed roles; neither crosses to the other roster.
- The Claude Code **resume-picker** clutter (orphaned `*.jsonl` files) is a SEPARATE
  concern from khimaira sessions — handled by the `roster` script's session auto-prune,
  not this command.
- If the daemon is unreachable (`session_list` fails), report plainly — don't guess.
