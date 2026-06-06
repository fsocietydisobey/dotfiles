# /khimaira-presence-check — ping all roster members and verify active + connected

Checks every member of the active roster chat: alive, reachable (SSE connected), and obligation-clean. Surfaces dark/deaf/stalled sessions.

## Steps

1. Resolve roster chat — chat_my_chats(session_id=<my_id>) to find active chat_id.

2. Per-member check (parallel) for each member:
   - session_summary(session_id=<id>) — last_active_age_s, status, decisions
   - chats.is_reachable(session_id) via themis_check probe

3. Classify each using the 2×2 (reachable × active):
   - HEALTHY: last_active < 600s, no issues → no action
   - IDLE: last_active > 600s, no obligations → OK (holding)
   - ALIVE-BUT-DEAF: recently active but SSE dropped → ping to re-register
   - DARK: last_active > 2700s AND unreachable → flag for respawn/drop
   - OBLIGATION-STALLED: open obligation + silent > T → escalate to master

   ⚠️ INTERIM: false-dark-prone until #7's disk-WIP work-signal lands; a deaf-but-working
   session may be misclassified DARK. TODO: swap last_active for #7's hook-independent
   disk-WIP check (owed-task target-file mtime + cwd working-tree scan).

4. Print a presence table with per-session status.

5. Send targeted pings to ALIVE-BUT-DEAF sessions:
   session_post_notice(target=<id>, text="⚡ Presence check: call chat_my_chats to re-register SSE.")

6. Print summary: count of healthy / idle / deaf / dark / stalled.
