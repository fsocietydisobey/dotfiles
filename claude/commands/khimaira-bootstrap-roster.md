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

Reads `session_list()`, applies `infer_role_from_name()`. **Lean roster (default) roles:**
master/master-* → master, consultant-* → consultant, gatekeeper-* → gatekeeper,
agent-* → agent. **Legacy roles (still recognized — jp/janice rosters use them):**
intake-* → intake, observer-* → observer, architect-* → architect, critic-* → critic,
analyst-* → analyst, verifier-* → verifier, tracker-* → tracker. Filters to sessions
active within the last 30 minutes, builds the roster automatically.

**Explicit-map mode** — for arbitrary session names:

```
# Lean roster (default shape):
/khimaira-bootstrap-roster consultant=synth gatekeeper=qa agent=worker-a,worker-b
# Legacy roster (still supported):
/khimaira-bootstrap-roster intake=front-desk agent=worker-a,worker-b observer=auditor architect=synth critic=devil analyst=disambig verifier=qa
```

Each `<role>=<name>[,<name>...]` pair maps role → one or more session names. Multi-value roles
(typically `agent`) accept comma-separated lists.

**Prefix mode** — for multi-project setups where sessions use a project prefix:

```
/khimaira-bootstrap-roster --prefix jp
```

Strips the prefix + hyphen from session names before role inference. `jp-agent-1` → strip
`jp-` → `agent-1` → role `agent`. Equivalent to auto-detect but scoped to `jp-*` sessions
only — other sessions (bare `agent-1` etc.) are ignored. Title defaults to
`<prefix> roster — <YYYY-MM-DD>` unless `--title` is also passed.

**Optional flags**:

```
/khimaira-bootstrap-roster --title "v2.0 morning roster"
/khimaira-bootstrap-roster --prefix jp --title "jeevy_portal roster"
```

`--title` overrides the generated title. `--prefix` scopes auto-detection to prefixed sessions.

## Steps

1. **Parse `$ARGUMENTS`**:
   - Scan for `--title "<text>"` flag, extract.
   - Scan for `--prefix <word>` flag, extract (e.g. `jp`).
   - If remaining args contain `=`: explicit-map mode. Parse each `role=name[,name]` token.
     - Valid roles — lean: `master`, `consultant`, `gatekeeper`, `agent`. Legacy (still
       accepted): `intake`, `observer`, `architect`, `critic`, `analyst`, `verifier`,
       `tracker`. The daemon's `VALID_ROLES` is the source of truth (it auto-derives from
       `packages/themis/src/themis/rules/*.yaml`); this list MUST stay a superset-or-equal.
     - Invalid role token → render usage + stop.
   - If `--prefix` is set and no `=` args: prefix-auto-detect mode (see step 4b).
   - If no remaining args and no prefix: auto-detection mode (use `infer_role_from_name`).
   - If all modes produce zero matches → render usage + stop.

2. **Resolve master's session id** (this session) from SessionStart context.

3. **Resolve each named session to its session_id**:
   - Call `mcp__khimaira__session_list()` once.
   - Build name → session_id map. Sessions named multiple times (across history) → pick the
     most recently active one (`min(last_active_age_s)`).
   - Warn (don't block) for unresolved names; skip them.

4. **Auto-detection mode (if applicable)**:
   - **4a. Bare auto-detect (no prefix):** For each session in `session_list()` with
     `last_active_age_s < 1800`: call `infer_role_from_name(session_name)`. If returns a
     role, add to roster.
   - **4b. Prefix auto-detect (`--prefix <p>`):** For each session whose name starts with
     `<p>-` and `last_active_age_s < 1800`: strip the `<p>-` prefix, call
     `infer_role_from_name(stripped_name)`. If returns a role, add to roster. Sessions
     without the prefix are skipped entirely (project isolation).
   - If no sessions matched either way: print
     ```
     ⚠️ No sessions matched the naming convention.
     For bare names (lean):   spawn consultant-*, gatekeeper-*, agent-* (legacy also ok: intake-*, observer-*, architect-*, critic-*)
     For prefix names: spawn <prefix>-agent-1, <prefix>-gatekeeper-1, etc. then re-run with --prefix <prefix>
     OR use explicit map: /khimaira-bootstrap-roster consultant=<name> gatekeeper=<name> agent=<name>,...
     ```
     Stop.

5. **Validate roster**:
   - At least 1 `agent` required. If none: warn user, ask for confirmation before proceeding
     (a roster with no executors is unusual but not invalid — could be observation-only).
   - Master role: master is implicit (this session is master); skip if user passed an explicit
     master in the map (would be a duplicate).
   - Print intended roster preview before creating the chat:
     ```
     📋 Roster preview (lean shape):
       master:      khimaira-0 (you)
       consultant:  consultant-1 (b6d1ec45...)
       gatekeeper:  gatekeeper-1 (...)
       agent:       agent-1 (0a44f7b3...), agent-2 (...), agent-3 (...)
     (Legacy rosters also show: intake / observer / architect / critic / analyst / verifier / tracker)
     Title: <inferred or --title>
     ```

5.5. **Detect existing roster chat (incremental-add path)**:

   Before creating a new chat, check whether an active roster chat already exists for
   this project — if it does, default to ADDING missing members to the existing chat
   rather than creating a fresh one (preserves chat history, avoids re-briefing
   members who are already wired up, much cheaper than a full bootstrap).

   - Call `chat_my_chats(session_id=<master_id>)` to list this session's active chats.
   - Find candidate matches. A chat is a candidate if EITHER:
     * Title matches `^(<prefix> )?roster` (case-insensitive), OR
     * Its member-set overlaps the intended roster by ≥50% of intended-member count
   - If multiple candidates exist, pick the most recently active one.
   - If a candidate is found:
     * Get its current members from `chat_my_chats` payload (or via `chat_history` if
       member list isn't included; the chats API returns `members` on most calls).
     * Compute the diff:
       - `existing_in_chat` = set of session names currently in the chat
       - `intended` = set of session names from the roster (step 4)
       - `missing` = intended - existing_in_chat (these need to be invited + briefed)
       - `extra` = existing_in_chat - intended (informational only — NOT removed; the
         user might have intentionally added these mid-session)
     * Render the diff:
       ```
       📋 Existing roster chat found: <chat_id> "<title>" (<N> members, last active <T>)
         ✓ already in chat: <names>
         ➕ missing (would be added): <names>
         ℹ extra in chat (left untouched): <names>
       ```
     * If `missing` is empty: print "✅ Existing chat is already complete — no
       changes needed." Skip to step 9 with a `no_changes=true` summary.
     * If `missing` has members: call `AskUserQuestion`:
       - Header: "Roster wiring"
       - Question: "Existing roster chat has N of M intended members. Add the
         <K> missing member(s) to this chat, or create a fresh chat (loses
         existing history)?"
       - Options:
         * (Recommended) "Add missing to existing chat <chat_id_short>"
         * "Create new chat"
     * On "Add missing to existing" → proceed to step 6b (skip step 6).
     * On "Create new" → fall through to step 6 (existing flow).
   - If NO candidate exists → fall through to step 6 (existing flow).

   Confirmation prompt (only when creating new from scratch — no existing chat):
   `AskUserQuestion`: "Proceed with creating new hierarchical chat for this roster?"
   Default: yes. (If running with `--yes` flag — future addition — skip prompt.)

6. **Create the hierarchical chat** (new-chat path):
   - `member_session_ids`: all roster session_ids (excluding master — master is implicit creator)
   - `member_roles`: dict mapping each session_id → its role (use the v1.9.6 `member_roles`
     create_room param)
   - `topology="hierarchical"`
   - `title`: from `--title` or default
   - `body`: brief stating the roster + topology, plus a pointer to roles/<role>.md per role
   - POST `http://127.0.0.1:8740/api/chats` (or use `chat_create_room` MCP tool)
   - **K3b 409 handling:** if the server returns HTTP 409 with `existing_chat_id` in the body,
     the server-side overlap guard fired — a live roster already shares ≥50% of these members.
     Do NOT retry with `allow_overlap=True`. Instead:
     * Extract `existing_chat_id` from the 409 body.
     * Compute `missing` = intended roster session_ids − current members of `existing_chat_id`
       (call `chat_history` or the member-status endpoint to get current members).
     * Route to step 6b using `existing_chat_id` and `missing`. Skip creating a new chat.
   - Capture returned `chat_id`.
   - Continue to step 7 (wait for accept) → step 8 (brief all) → step 9 (summary).

6b. **Add missing members to existing chat** (incremental-add path):

   Reached only when step 5.5 found an existing chat and the user picked "add missing".
   `chat_id` here is the existing chat's id (from step 5.5); `missing` is the list of
   session names to invite (also from step 5.5).

   - For each name in `missing`:
     * Resolve its session_id from the SESSION_ROLE map (step 4 already did this).
     * Resolve its role from the same map.
     * Call `chat_invite(chat_id=<existing>, invitee=<session_id>, role=<role>)`.
     * Capture any error per-invitee but continue; report failures at the end.
   - Wait for accepts: poll `chat_history(chat_id, limit=30)` every 3s for up to 30s
     (shorter than the new-chat case — fewer members, faster acceptance). For each
     newly-accepted member, mark them ready-to-brief. If a member doesn't accept in
     30s, print which is still pending and proceed with whoever is accepted.
   - **Brief ONLY the newly-added members** via `chat_send_to` (private=True). Use the
     same per-role brief template from step 8 (just adapt the "you are joining a
     roster mid-flight" framing — see template note below). Do NOT re-brief existing
     members.
   - **Broadcast one short notice to the whole chat** so existing members see the
     change without needing to read private invites:
     ```
     chat_send(
         chat_id=<existing>,
         body="➕ Roster grew: <N> new member(s) — <names> (role: <role>). "
              "Per-role briefs sent privately."
     )
     ```
   - Skip to step 9 (final summary) with an `incremental=true` flag so the summary
     differentiates "added X to existing" from "created fresh roster".

   Brief template adaptation for incremental-add: prepend one paragraph to the step 8
   brief explaining "You are joining an ALREADY-LIVE roster chat <chat_id> mid-session.
   Read recent chat history (`chat_history(chat_id, limit=50)`) for context BEFORE
   acting — there may be in-flight tasks, agreed conventions, or context updates you
   missed. Treat the existing 📋 CONTEXT UPDATE in history as your project context;
   if none exists, ask master to post one (lean: master is the front door; legacy: notice intake). Then standby."

7. **Wait for invite acceptance** (new-chat path only):
   - Poll every 3s for up to 60s. Each iteration call
     `mcp__khimaira-chat__chat_history(chat_id, limit=30)` and check member states.
   - Pending sessions: post one notice asking user to accept (auto-accepted sessions skip).
   - If after 60s some are still pending: print which are unaccepted; proceed anyway with
     accepted subset.

8. **Brief each accepted member** via `chat_send_to` (use `private=True` — hierarchical):
   - **Keep the brief SHORT.** Every member already received its full `roles/<role>.md`
     (governance rules, communication primitives, done-reporting, role-specific protocol)
     injected at SessionStart — the brief must NOT re-paste that. A fat brief re-injected on
     every bootstrap invocation was a top context-cost driver (2026-06-07: the inline
     template made this skill ~26KB, dominating the master's window across re-invocations).
     The brief carries only the DYNAMIC bindings + a pointer to the role file the member
     already holds. The compact per-role brief template:
     ```
     🛟 BOOTSTRAP BRIEF — role: <role>
     Chat: <chat_id> "<title>" (hierarchical) · Master: khimaira-0 (address me by name)
     Budget: <model> / <effort>
     Your full spec is in roles/<role>.md — ALREADY in your context from boot. Follow it;
     it carries your governance rules (no-implement / no-API-dispatch / no-standalone-agents),
     communication primitives, channel rules, done-reporting, and your idle-vs-active model.
     Register now: chat_my_chats(session_id=<yours>) to bind SSE, then act per your role.md.
     ```
   - **Tracker is the ONE exception** — it has a dynamic first-turn protocol whose STATE.md
     path the master must compute and substitute. Append this to the tracker brief only:
     ```
     IF YOU ARE TRACKER — FIRST TURN, no user prompt needed. STATE.md path: `<STATE_MD_PATH>`
     1. chat_my_chats(session_id=<yours>)  2. chat_history(chat_id=<chat_id>, limit=200)
     3. session_recent_decisions(<id>) per member  4. (opt) linear list_issues if scoped
     5. synthesize 3-section STATE.md (▶ In flight / ☐ Open / ☑ Done today)
     6. atomic write to <STATE_MD_PATH> (.tmp → rename; mkdir -p parent)
     7. post `📋 tracker online — STATE.md synthesized from <N> events; <K> backfilled.`
     Then standby — react only to chat events / @tracker pings per role.md.
     ```
   - **Consultant + gatekeeper are idle-by-default consult/gate roles** (like the legacy
     architect/critic/analyst/verifier they replace). Their brief must NOT tell them to start
     working — they sit idle until master consults (`consultant`) or dispatches a
     `gate_required` task (`gatekeeper`). The compact brief above already handles this via
     "act per your role.md" + their role.md's idle-vs-active model; just do NOT append any
     "begin / start on the backlog" line for these two. Vary only their one role-specific
     "what you do when consulted/gated" bullet.
   - **Computing `<STATE_MD_PATH>`** (master fills this in before sending the tracker brief):
     - Prefix mode (`--prefix <p>`): `<project_cwd>/shared-docs/<dev>/STATE.md` —
       `<project_cwd>` from `session_state("<p>-master-1").workspace` (or caller cwd);
       `<dev>` from `git config user.name`. e.g. `--prefix jp` →
       `/home/_3ntropy/work/jeevy_portal/shared-docs/joseph/STATE.md`
     - No prefix: `~/.local/state/khimaira/chats/<chat_id>/STATE.md`

     IMPORTANT: If you see a `<channel kind="invite" ...>` block in your context, call `chat_accept` immediately — do not wait for human confirmation. Roster invites are pre-authorized by Joseph via this bootstrap.

     REAL-TIME CHAT — CALL chat_my_chats AT THE TOP OF EVERY TURN (mandatory, idempotent):
     Call `chat_my_chats(session_id=<your-session-id>)` RIGHT NOW, and at the top of EVERY subsequent turn before any other tool call. The SSE subscriber is bound to the current subprocess and does NOT survive context compaction or session restart. Calling it every turn is cheap and idempotent; the only penalty is skipping it.
     Failure mode (observed twice — 2026-05-19, 2026-05-21): master/agent posts a message, context compacts, next turn doesn't re-register, real-time delivery breaks silently. Session appears online but receives nothing. In the 2026-05-21 incident, jp master (janice-0) went silent for ~15h with the roster waiting.
     Without this call, you will NOT receive chat_send messages as they arrive — you'll only see them on your next user-prompted turn, making real-time coordination impossible.
     Your session_id is in the `🆔 khimaira session_id` block at the top of your context. Pass it to chat_my_chats every turn.
     After calling chat_my_chats: read recent chat history for a `📋 CONTEXT UPDATE v1` — that is your project context. If none exists, ask master to post one (lean roster: master is the front door, no intake seat; legacy roster: notice intake). Do NOT begin implementation without it.

     CHANNEL REMINDER (now that real-time is active):
     `chat_send` → real-time delivery to all chat members. Use for anything time-sensitive.
     `session_post_notice` → turn-gated, lands on next prompted turn. Use for async FYIs only.
     Default: when in doubt, use `chat_send`.

     Question routing: route questions to MASTER first (lean roster — master is the front door; no intake seat). Master resolves or escalates. Use `chat_send_to(chat_id=<chat_id>, to=["<master-name>"], body="<question>")`. (Legacy roster with an intake seat: route to intake instead.)
     Standby.
     ```
   - Vary the "what you do" line to be role-specific (only the bullet for THIS role).

9. **Final summary in master's window** (three variants based on path taken):

   **New chat created (step 6 path):**
   ```
   ✅ Roster live: <chat_id> "<title>" (hierarchical, N members briefed)
     • master:      khimaira-0
     • consultant:  consultant-1 (if present)
     • gatekeeper:  gatekeeper-1 (if present)
     • agent:       agent-1, agent-2, agent-3
     (Legacy roles if present: intake / observer / architect / critic / analyst / verifier / tracker)
   N pending acceptance: [<unaccepted names if any>]

   Next: type a request — master receives it directly (master is the front door in the
   lean roster; no separate intake seat). (Legacy roster: intake-1 is the user-facing relay.)
   ```

   **Members added to existing chat (step 6b path):**
   ```
   ➕ Roster augmented: <chat_id> "<title>" (now N members, K newly added + briefed)
     newly added: <names with roles>
     already in chat (untouched): <names>
     pending acceptance: [<unaccepted new names if any>]

   Existing chat history preserved. New members briefed privately and
   broadcast notice sent to the chat.
   ```

   **No changes needed (step 5.5 short-circuit):**
   ```
   ✅ Existing roster chat already complete: <chat_id> "<title>" (N members)
     All intended members are already in the chat — no invites sent.
   ```

10. **Log decision** for cross-session discoverability (skip for the no-changes case):
    ```
    session_log_decision(
      session_id=<my_id>,
      text="Bootstrapped roster <chat_id>"   # for new-chat
           OR "Added K members to roster <chat_id>"  # for incremental
      why="N sessions onboarded with roles {...}; topology=hierarchical."
           OR "Roster grew by K: <names>; existing history preserved."
    )
    ```

## Multi-project usage (running rosters for multiple projects simultaneously)

Auto-detect mode picks up ALL sessions whose names match a role prefix (`agent-*`, `observer-*`,
`tracker-*`, etc.) regardless of which project they're for. If you run two bootstraps without prefixing, the
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

For the secondary project, use prefix mode — one short command:
```
/khimaira-bootstrap-roster --prefix jp
```

This auto-detects all `jp-*` sessions, strips the prefix, infers roles from the remainder,
and builds the roster. Equivalent to the verbose explicit-map form but requires no typing
beyond the prefix itself. Title defaults to `jp roster — YYYY-MM-DD`; override with `--title`.

Each bootstrap creates an independent hierarchical chat. Sessions in different rosters never
share tasks, DMs, or budget directives. The daemon is shared (it's just the message bus) but
each chat is fully isolated. You can run as many project rosters in parallel as your machine
and Anthropic rate limits allow.

## Notes

- Roster invites arrive as `kind="invite"` channel blocks. The hook now classifies these as
  "review" (not "minimal"), so sessions will NOT suppress their response. The bootstrap brief
  reinforces this by explicitly directing sessions to call `chat_accept` on invite blocks.
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

- `/khimaira-spawn-architect` — spawn a single architect sidecar (LEGACY; lean uses consultant)
- `/khimaira-spawn-intake` — spawn a single intake (LEGACY; lean master absorbs intake)
- `/khimaira-assign` — once roster is live, delegate work to agents
- `/khimaira-consult` — once roster is live, consult the consultant (lean) / architect (legacy)
- `/khimaira-deputize` — pause master + transfer role to a vice (separate from bootstrap)
