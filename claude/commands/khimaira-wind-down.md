# /khimaira-wind-down — wind down the roster to a stable checkpoint for the day

Brings all in-flight work to a clean stop, posts a handoff, sets the wind-down sentinel, and notifies all roster members to stand down.

## Steps

1. Set the wind-down sentinel — set_roster_wind_down(True) (suppresses Guard-4/Guard-5 overnight alarms).

2. Gather in-flight state:
   - session_list() filtered to active roster members
   - chat_history(roster_chat, limit=50) — recent task status, any open gates
   - session_recent_decisions(my_id, limit=20)

3. For each agent with in_progress tasks:
   - Post a notice: "🌙 Wind-down: please finish your current step, post a done/progress update to the roster chat, and stand down. Do NOT start new tasks."
   - Wait up to 60s for their acknowledgement.

4. Build and post the wind-down handoff (via session_post_handoff, scope_cwd=project_root):
   ```
   🌙 WIND-DOWN CHECKPOINT — <date>

   ═══ RESUME FIRST STEPS ═══
   [Most urgent action on wake: pending gates, session restores, etc.]

   ═══ IN-FLIGHT AT WIND-DOWN ═══
   [Each agent's last known state + what they were working on]

   ═══ PENDING GATES ═══
   [Tasks done but awaiting approval]

   ═══ OPEN BACKLOG ═══
   [Priority-ordered list of pending work]

   ═══ ROSTER STATE ═══
   [Active chat_id, member list, any sessions to respawn on wake]

   ═══ KEY CONTEXT ═══
   [Non-obvious things next session needs to know]
   ```

5. Broadcast to roster chat:
   "🌙 Wind-down active. Sentinel set — Guard-4/Guard-5 suppressed overnight. Handoff posted for tomorrow's session. Everyone stand down."

6. Print confirmation: handoff_id, sentinel status, list of sessions standing down.

## When NOT to use
- Mid-task when an agent is in the middle of a critical operation (wait for a clean checkpoint)
- If a B3 gate just opened and the reviewer is about to post (let the gate close first)
