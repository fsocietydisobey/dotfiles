# /khimaira-wake-up — wake the roster from wind-down and resume from checkpoint

Reads the wind-down handoff, clears the sentinel, re-registers all sessions, and resumes in-flight work from the checkpoint.

## Steps

1. Lift the wind-down sentinel — set_roster_wind_down(False). Guards resume monitoring.

2. Re-register SSE — chat_my_chats(session_id=<my_id>).

3. Consume the wind-down handoff — session_consume_handoffs(session_id=<my_id>, cwd=<project_root>). Read it fully.

4. Run a presence check — equivalent to /khimaira-presence-check: which sessions are alive, which are dark/dead and need respawning.

   ⚠️ INTERIM: false-dark-prone until #7's disk-WIP work-signal lands; a deaf-but-working
   session may be misclassified DARK. TODO: swap last_active for #7's hook-independent
   disk-WIP check (owed-task target-file mtime + cwd working-tree scan).

5. For each session that was in-flight at wind-down:
   - If alive: post a notice: "☀️ Wake-up: resume your task from the wind-down checkpoint. Check your inbox for context."
   - If dark/dead: note for master to respawn.

6. Print the resume brief to master's window:
   ```
   ☀️ ROSTER WAKE-UP — <date>

   Sentinel: LIFTED ✅
   Handoff: <handoff_id> loaded

   FIRST ACTIONS:
   [From the handoff's RESUME FIRST STEPS section]

   ROSTER STATUS:
   [Per-session: alive/deaf/dead + what to do]

   PENDING GATES:
   [Any gates that need immediate attention]

   BACKLOG (ordered):
   [Priority list from the handoff]
   ```

7. Ask master: "Ready to proceed? Type YES to begin dispatching or specify what to start with."

## When to use
- First thing after a wind-down (before any other work)
- After a daemon restart wiped session state
- When resuming a roster that's been idle overnight
