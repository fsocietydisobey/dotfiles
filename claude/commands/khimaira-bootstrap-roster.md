# /khimaira-bootstrap-roster [<map>] — onboard a fresh role-typed roster in one call

Master-side: take a set of pre-spawned sessions, infer or accept role assignments, create a
hierarchical chat with all of them as accepted members + role-bound, brief each, and return
"✅ roster live." Designed for the morning-after workflow when you've spawned a fresh set of
windows overnight and want master to wire them up in one command.

## Why this exists

The manual onboarding flow (create chat → invite each → wait for accept → assign roles → brief
each → fire test) is ~10 master operations and several chat round-trips. This skill collapses
that into a single command. Pairs with the role.md auto-loading wire-up so each session boots
with its role binding.

## Args

**Auto-detection mode (no args)** — uses the naming convention:

```
/khimaira-bootstrap-roster
```

Reads `session_list()`, applies `infer_role_from_name()` (intake-* → intake, agent-* → agent,
observer-* → observer, architect-* → architect, critic-* → critic, master/master-* → master),
filters to sessions active within the last 30 minutes, builds the roster automatically.

**Explicit-map mode** — for arbitrary session names:

```
/khimaira-bootstrap-roster intake=front-desk agent=worker-a,worker-b observer=auditor architect=synth critic=devil
```

Each `<role>=<name>[,<name>...]` pair maps role → one or more session names. Multi-value roles
(typically `agent`) accept comma-separated lists.

**Optional title flag**:

```
/khimaira-bootstrap-roster --title "v2.0 morning roster"
```

If omitted, generates a title like `roster — <YYYY-MM-DD>`.

## Steps

1. **Parse `$ARGUMENTS`**:
   - Scan for `--title "<text>"` flag, extract.
   - If remaining args contain `=`: explicit-map mode. Parse each `role=name[,name]` token.
     - Valid roles: `intake`, `agent`, `observer`, `architect`, `critic`, `master`.
     - Invalid role token → render usage + stop.
   - If no remaining args: auto-detection mode (use `infer_role_from_name`).
   - If both explicit map and auto detection produce zero matches → render usage + stop.

2. **Resolve master's session id** (this session) from SessionStart context.

3. **Resolve each named session to its session_id**:
   - Call `mcp__khimaira__session_list()` once.
   - Build name → session_id map. Sessions named multiple times (across history) → pick the
     most recently active one (`min(last_active_age_s)`).
   - Warn (don't block) for unresolved names; skip them.

4. **Auto-detection mode (if applicable)**:
   - For each session in `session_list()` with `last_active_age_s < 1800`:
     - Call `infer_role_from_name(session_name)` (imported from `khimaira.monitor.chats`)
     - If returns a role: add `(session_id, name, role)` to roster
   - If no sessions matched: print
     ```
     ⚠️ No sessions matched the naming convention.
     Either spawn sessions following: intake-*, agent-*, observer-*, architect-*, critic-*
     OR re-run with explicit map: /khimaira-bootstrap-roster intake=<name> agent=<name>,...
     ```
     Stop.

5. **Validate roster**:
   - At least 1 `agent` required. If none: warn user, ask for confirmation before proceeding
     (a roster with no executors is unusual but not invalid — could be observation-only).
   - Master role: master is implicit (this session is master); skip if user passed an explicit
     master in the map (would be a duplicate).
   - Print intended roster preview before creating the chat:
     ```
     📋 Roster preview (about to create hierarchical chat):
       master:    khimaira-0 (you)
       intake:    intake-1 (b6d1ec45...)
       agent:     agent-1 (0a44f7b3...), agent-2 (...), agent-3 (...)
       observer:  observer-1 (...)
       architect: architect-1 (...)
       critic:    critic-1 (...)
     Title: <inferred or --title>

     Proceed? Type "go" to confirm or any other input to abort.
     ```
   - Wait for user "go". (If running with `--yes` flag — future addition — skip prompt.)

6. **Create the hierarchical chat**:
   - `member_session_ids`: all roster session_ids (excluding master — master is implicit creator)
   - `member_roles`: dict mapping each session_id → its role (use the v1.9.6 `member_roles`
     create_room param)
   - `topology="hierarchical"`
   - `title`: from `--title` or default
   - `body`: brief stating the roster + topology, plus a pointer to roles/<role>.md per role
   - POST `http://127.0.0.1:8740/api/chats` (or use `chat_create_room` MCP tool)
   - Capture returned `chat_id`.

7. **Wait for invite acceptance**:
   - Poll every 3s for up to 60s. Each iteration call
     `mcp__khimaira-chat__chat_history(chat_id, limit=30)` and check member states.
   - Pending sessions: post one notice asking user to accept (auto-accepted sessions skip).
   - If after 60s some are still pending: print which are unaccepted; proceed anyway with
     accepted subset.

8. **Brief each accepted member** via `chat_send_to`:
   - Per-role briefing message (use `private=True` since we're in hierarchical mode):
     ```
     🛟 BOOTSTRAP BRIEF — you are: <role>
     Chat: <chat_id> "<title>" (topology: hierarchical)
     Master: khimaira-0 (you can address me by name in chat)
     Role file: packages/khimaira/src/khimaira/roles/<role>.md
     Recommended budget: <model> / <effort>

     What you do (read your role .md for details):
     - intake: receive user requests; format 🎯 INTAKE HANDOFF specs to master
     - agent: receive /khimaira-assign tasks from master; execute on begin signal
     - observer: read-only audit; surface anomalies to master
     - architect: idle until consulted via /khimaira-consult
     - critic: invited ad-hoc by master to challenge designs

     Read tasks/v1.9-orchestration/{STATE,USAGE}.md for full context.
     Standby.
     ```
   - Vary the "what you do" line to be role-specific (only the bullet for THIS role).

9. **Final summary in master's window**:
   ```
   ✅ Roster live: <chat_id> "<title>" (hierarchical, N members briefed)
     • master:    khimaira-0
     • intake:    intake-1
     • agent:     agent-1, agent-2, agent-3
     • observer:  observer-1
     • architect: architect-1
     • critic:    critic-1
   N pending acceptance: [<unaccepted names if any>]

   Next: type a request — intake-1 will receive it via the user-facing flow.
   (Or address master directly to bypass intake.)
   ```

10. **Log decision** for cross-session discoverability:
    ```
    session_log_decision(
      session_id=<my_id>,
      text="Bootstrapped roster <chat_id>",
      why="N sessions onboarded with roles {...}; topology=hierarchical."
    )
    ```

## Multi-project usage (running rosters for multiple projects simultaneously)

Auto-detect mode picks up ALL sessions whose names match a role prefix (`agent-*`, `observer-*`,
etc.) regardless of which project they're for. If you run two bootstraps without prefixing, the
same sessions end up in both rosters and receive tasks from two masters simultaneously — context
collision.

**The fix: use project-scoped session names for any project that isn't your primary.**

```
# Primary project (e.g. khimaira) — bare role names, auto-detect works:
agent-1, agent-2, observer-1, architect-1, intake-1

# Secondary project (e.g. jeevy_portal) — project-prefixed:
jp-agent-1, jp-agent-2, jp-observer-1, jp-architect-1
```

`infer_role_from_name("jp-agent-1")` → prefix `jp` → not in ROLE_BUDGET → skipped by
auto-detect. The jp-* sessions are invisible to the khimaira bootstrap.

For the secondary project, use explicit-map mode:
```
/khimaira-bootstrap-roster agent=jp-agent-1,jp-agent-2 observer=jp-observer-1 \
    architect=jp-architect-1 --title "jeevy_portal roster"
```

Each bootstrap creates an independent hierarchical chat. Sessions in different rosters never
share tasks, DMs, or budget directives. The daemon is shared (it's just the message bus) but
each chat is fully isolated. You can run as many project rosters in parallel as your machine
and Anthropic rate limits allow.

## Notes

- Role.md auto-loading is live (v1.9.6) — sessions see their `📖 ROLE FILE` block at boot.
- The skill uses `topology="hierarchical"` by default — DMs default to private. If you want a
  flat-mode roster (broadcast everything), pass `--topology flat` (future flag).
- Idempotency: if a chat with the same title already exists and is active, the skill should
  detect + ask whether to add to existing or create new. (Implementation: defer; v1 just always
  creates new.)
- For sessions that don't match any role pattern AND aren't in the explicit map → silently
  excluded from the roster. Print them in the preview as "skipped: <names>" so user can see.

## When NOT to use

- Single-session debugging (no roster needed)
- Ad-hoc 1:1 conversations (use `/khimaira-chat <peer>` directly)
- When you want a flat-topology chat (this skill defaults to hierarchical)

## See also

- `/khimaira-spawn-architect` — spawn a single architect sidecar (architect-only flow)
- `/khimaira-spawn-intake` — spawn a single intake (intake-only flow)
- `/khimaira-assign` — once roster is live, delegate work to agents
- `/khimaira-consult` — once roster is live, consult the architect
- `/khimaira-deputize` — pause master + transfer role to a vice (separate from bootstrap)
