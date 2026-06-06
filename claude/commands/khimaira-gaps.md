# /khimaira-gaps — show pending khimaira platform gap reports

Filters the khimaira project's handoff backlog for `🐞 KHIMAIRA GAP` tagged items and
displays them as a clean view, avoiding the ~570 stale Guard-5 handoffs in the same
channel.

## Why this exists

Platform gaps from roster agents are forwarded to the khimaira project via
`session_post_handoff(scope_cwd=/home/_3ntropy/dev/khimaira)` with a `🐞 KHIMAIRA GAP`
tag. That channel is shared with ~570 stale Guard-5 gate-handoffs. Without a filter,
gaps are swallowed by noise — the same failure mode that lost janice's gap report.
This command is the read-side that makes the write-side useful.

## Steps

1. Call `session_consume_handoffs(session_id=<my_id>, cwd="/home/_3ntropy/dev/khimaira")`
   to pull all pending handoffs for the khimaira project.

2. Filter for entries whose text contains `🐞 KHIMAIRA GAP`.

3. If none found, also call `session_search_archive(cwd=..., query="🐞 KHIMAIRA GAP")`
   as a fallback (catches already-claimed ones).

4. Display the filtered results, newest first:
   ```
   🐞 KHIMAIRA GAP REPORT — <date>
   Found: N open gap(s) in ~/dev/khimaira handoff backlog

   [1] area: <area> | from: <from_session> | <ts>
       <desc>
       repro: <if provided>

   [2] ...
   ```

5. If no gaps found: "📭 No 🐞 KHIMAIRA GAP handoffs found in ~/dev/khimaira. Either none
   have been filed, or they were already claimed and acted on. Check the archive with
   `/khimaira-gaps archive` if needed."

## Notes

- **Roster invariant:** `scope_cwd` is a project discriminator, not a per-session one.
  This command surfaces gaps for ANY session working in the khimaira repo, not only a
  dedicated khimaira-dev seat. In a product roster sitting in the same checkout, this
  is cross-surface — use the tag filter; don't act on items outside your lane.
- **Noise source:** The ~570 non-gap handoffs are stale Guard-5 gate-alerts. Guard-5
  is disabled (KHIMAIRA_GUARD5=0) so no new ones are minted. A one-time GC of stale
  Guard-5 handoffs would clean the channel but is not required for this filter to work.
- **Filing new gaps:** if you discover a khimaira platform gap, report it to your master
  via the roster chat with the format `🐞 KHIMAIRA GAP [area: ...] — desc — repro: ...`.
  Master forwards it via `session_post_handoff`; this command then surfaces it here.
