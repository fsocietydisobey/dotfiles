# /tasks — show open tasks from every configured task source

Surface "what's on my plate" by fanning out across every task source
configured in `~/.khimaira/task_sources.yaml`. Includes adapters that
the SessionStart hook can't reach — Linear-style sources that need
MCP / network are called from agent context here.

The SessionStart hook ALREADY surfaces hook-safe sources (default
JSONL adapter, GitHub Issues via `gh`) at boot. `/tasks` is for:

- explicitly re-checking after the boot block scrolled away
- including non-hook-safe sources (e.g. Linear adapter once
  daemon-side dispatch lands)
- the user asking "what's open?" mid-session

## Steps

1. Call `mcp__khimaira__list_tasks(hook_safe_only=false)`.
2. Render the returned string verbatim. The tool already formats with
   the standard `📋 khimaira tasks — N open assignment(s):` header
   and per-task bullets matching the SessionStart hook's layout, so
   no further re-templating is needed.
3. If the output starts with `📭 no open tasks`, just show that and stop.
4. If the user passed an argument (`$ARGUMENTS`), interpret it as a
   filter substring — show only tasks whose `id`, `title`, or
   `source` contains the substring (case-insensitive). Surface the
   filter in your response: "Filtered to N task(s) matching `<arg>`."

## Notes

- This command is read-only. It does NOT create, update, or close
  tasks. Adapter authors decide whether their source supports writes;
  khimaira's protocol is read-only at the Task surface.
- If the daemon isn't running, the MCP tool may still succeed (the
  task-source code runs in-process inside the MCP server, not against
  the daemon). The daemon dependency is only relevant for adapters
  that hit the daemon for caching — none today.
- Misconfigured sources log a warning to `khimaira.log` and return
  `[]` for that source — they don't poison the whole list. So a
  partial result is the normal degraded state.

## When the user wants to ADD a task

This command doesn't write. For the default JSONL adapter, the user
edits `~/.khimaira/todo.jsonl` directly:

```jsonl
{"id":"local-1","title":"Wire up cache pricing","state":"in progress"}
{"id":"local-2","title":"Document the protocol","state":"todo"}
```

For external trackers, the user creates the task in the source
(Linear UI, `gh issue create`, etc.) — khimaira surfaces what
already exists.
