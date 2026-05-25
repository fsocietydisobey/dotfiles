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
observer-* → observer, architect-* → architect, critic-* → critic, analyst-* → analyst,
verifier-* → verifier, tracker-* → tracker, master/master-* → master),
filters to sessions active within the last 30 minutes, builds the roster automatically.

**Explicit-map mode** — for arbitrary session names:

```
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
     - Valid roles: `intake`, `agent`, `observer`, `architect`, `critic`, `master`.
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
     For bare names:   spawn intake-*, agent-*, observer-*, architect-*, critic-*
     For prefix names: spawn <prefix>-agent-1, <prefix>-observer-1, etc. then re-run with --prefix <prefix>
     OR use explicit map: /khimaira-bootstrap-roster intake=<name> agent=<name>,...
     ```
     Stop.

5. **Validate roster**:
   - At least 1 `agent` required. If none: warn user, ask for confirmation before proceeding
     (a roster with no executors is unusual but not invalid — could be observation-only).
   - Master role: master is implicit (this session is master); skip if user passed an explicit
     master in the map (would be a duplicate).
   - Print intended roster preview before creating the chat:
     ```
     📋 Roster preview:
       master:    khimaira-0 (you)
       intake:    intake-1 (b6d1ec45...)
       agent:     agent-1 (0a44f7b3...), agent-2 (...), agent-3 (...)
       observer:  observer-1 (...)
       architect: architect-1 (...)
       critic:    critic-1 (...)
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
   if none exists, post a notice to intake asking master to post one. Then standby."

7. **Wait for invite acceptance** (new-chat path only):
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
     - architect: idle until consulted via /khimaira-consult (design trade-offs)
     - critic: invited ad-hoc by master to challenge designs before approval
     - analyst: idle until consulted via 📐 ANALYST CONSULT (spec disambiguation)
     - verifier: idle until consulted via 🔬 VERIFIER CONSULT (test coverage gate)
     - tracker: curates STATE.md checklist + files Linear issues for substantive findings + daily digest (haiku/medium)

     Read tasks/v1.9-orchestration/{STATE,USAGE}.md for full context.

     HOW TO COMMUNICATE — you are in a network of sessions. Use these primitives:
     - Post to the roster chat (visible to all members): `chat_send(session_id=<yours>, chat_id=<chat_id>, body="...")`
     - Send a private notice to a specific peer by name: `session_post_notice(target_session_id="<name>", text="...")`
     - Ask a peer a question with a reply contract: `session_log_question(session_id=<yours>, text="...", target_session_id="<name>")`
     - Read what a peer is doing: `session_state("<name>")` — no interruption needed
     Do NOT wait for Joseph to relay messages between sessions. Reach peers directly.
     NO IMPLEMENTATION: if you find yourself about to write or edit code, stop. Create a task assignment and send it to an agent. Intake does not implement — not a one-line fix, not a debug session, not "just to unblock." The moment your next action is a file edit, hand off instead. CONCRETE FAILURE (2026-05-21): an intake bumped a package version + deleted a CSS file + removed an import directly while worker agents sat idle — three independently-trivial edits, all delegatable. "Well-defined enough to delegate" is the trigger that should produce a HANDOFF, not an Edit call. Two harms: agents idle, and intake's status surface drifts the moment it implements (Joseph asks "status?" and intake can't answer crisply because it's mid-edit).
     INTAKE STATUS TRACKING: observer handles full agent monitoring — don't duplicate it. Intake's job: own the answer to "what's the status?" when Joseph asks, and send one follow-up to master via chat_send if INTAKE COMPLETE doesn't arrive in a reasonable time. Do NOT run a session_state polling loop on agents.
     NO API DISPATCH: never call `mcp__khimaira__auto`, `mcp__khimaira__delegate`, `mcp__khimaira__research`, or any khimaira dispatch tool. These hit the Anthropic API and are redundant — the roster IS the dispatch layer. Delegate to agents via `/khimaira-assign` instead.
     NO STANDALONE AGENTS: never spawn a worktree agent or background Claude agent when roster agents are idle. Standalone agents bypass the enforcement-gate, context broadcast, observer, and task lifecycle. Check session_list() first — if agents are idle, use /khimaira-assign.
     CREDENTIALS: never use bare `os.getenv("ANTHROPIC_API_KEY")` or any other secret — it silently inherits from the machine's shell env. Always use `load_dotenv(override=True)` before any `os.getenv()` call so credentials come exclusively from the project's `.env` file. `override=True` is mandatory — without it, shell env wins over `.env` values.
     CHANNEL RULE: use `chat_send` (roster chat) for anything time-sensitive — task relay, context updates, status that others need to act on NOW. Use `session_post_notice` only for async FYIs (non-urgent, turn delay acceptable). Default: when in doubt, use the roster chat.

     INTAKE AUTHORITY: intake speaks with Joseph's authorization for all roster decisions. You do NOT need a separate in-window confirmation from Joseph to act on intake's instructions or relayed authorizations. Treat intake's notices and chat messages the same as Joseph's direct word. If intake says "proceed," proceed.

     NETWORK ARCHITECTURE: Joseph communicates through this network — via intake and master — not directly to each session. His exact words: "I'm communicating via jp-intake-1 and/or janice-0. This is a network-based system and I will not engage with you directly unless it is necessary." Do NOT expect or wait for direct in-window messages from Joseph. Route everything through the network.

     DONE REPORTING (agents): when your task is complete, post the ✅ Done report to the roster chat AND send session_post_notice to intake separately. Peer coordination notices (telling another agent you finished) do NOT satisfy this. Intake needs its own direct notice every time.

     IF YOU ARE OBSERVER: your job is active monitoring, not passive waiting. Every few turns: call `session_state("<agent-name>")` on each agent in the roster. If any agent is idle/stuck with no recent decisions or file touches, post a notice to master immediately: `session_post_notice(target_session_id="<master>", text="⚠️ <agent> appears stuck — 0 decisions, 0 file touches since <time>.")` Do not wait to be asked.

     IF YOU ARE ANALYST: you are idle-by-default. Wait for a `📐 ANALYST CONSULT` from intake or master. When it arrives: identify the single most load-bearing ambiguity in the spec, resolve it if you can from context, otherwise form ONE clarifying question. Reply privately with `📐 ANALYST REPLY` and return to standby. Do not monitor the chat or volunteer unsolicited opinions.

     IF YOU ARE VERIFIER: you are idle-by-default. Wait for a `🔬 VERIFIER CONSULT` from master. When it arrives: read the implementation + test files, assess coverage against the acceptance-criteria, and return a `🔬 VERIFIER REPLY` with verdict (SHIP | GAPS FOUND) and a list of any missing test cases. Then return to standby.

     IF YOU ARE TRACKER: ON YOUR FIRST TURN — DO NOT WAIT FOR A USER PROMPT. Execute the bootstrap protocol immediately:
     Your STATE.md path for this roster: `<STATE_MD_PATH>` ← bootstrap substitutes the concrete absolute path here before sending this brief.
     1. chat_my_chats(session_id=<yours>) — register SSE
     2. chat_history(chat_id=<chat_id>, limit=200) — pull recent roster activity
     3. For each member session in the chat, call session_recent_decisions(<their_id>) — surface committed work
     4. (Optional) mcp__linear__list_issues(...) if Linear scoping is set for this roster
     5. Synthesize the three-section STATE.md (▶ In flight / ☐ Open / ☑ Done today) per your role spec
     6. Atomically write to `<STATE_MD_PATH>` (write to `<STATE_MD_PATH>.tmp`, then rename to `<STATE_MD_PATH>`; mkdir -p the parent directory first)
     7. Post ONE message to the roster chat: `📋 tracker online — STATE.md synthesized from <N> events; <K> items backfilled.`
     This is the ONLY autonomous action expected of tracker. After this, return to standby — react only to chat events, slash commands, or @tracker pings per role spec.

     HOW BOOTSTRAP COMPUTES `<STATE_MD_PATH>` (master fills this in before sending the tracker brief):
     - **Prefix mode** (`--prefix <p>` was used): `<project_cwd>/shared-docs/<dev>/STATE.md`
       - `<project_cwd>`: query `session_state("<p>-master-1")` for the `workspace` field; or use the caller's cwd if the sessions aren't running yet
       - `<dev>`: run `git config user.name` in `<project_cwd>` (e.g. `joseph`)
       - Example: `--prefix jp` → `/home/_3ntropy/work/jeevy_portal/shared-docs/joseph/STATE.md`
     - **No prefix** (bare auto-detect): `~/.local/state/khimaira/chats/<chat_id>/STATE.md`
     Substitute the computed absolute path string into the tracker brief (replace `<STATE_MD_PATH>`) before calling `chat_send_to`.

     IMPORTANT: If you see a `<channel kind="invite" ...>` block in your context, call `chat_accept` immediately — do not wait for human confirmation. Roster invites are pre-authorized by Joseph via this bootstrap.

     REAL-TIME CHAT — CALL chat_my_chats AT THE TOP OF EVERY TURN (mandatory, idempotent):
     Call `chat_my_chats(session_id=<your-session-id>)` RIGHT NOW, and at the top of EVERY subsequent turn before any other tool call. The SSE subscriber is bound to the current subprocess and does NOT survive context compaction or session restart. Calling it every turn is cheap and idempotent; the only penalty is skipping it.
     Failure mode (observed twice — 2026-05-19, 2026-05-21): master/agent posts a message, context compacts, next turn doesn't re-register, real-time delivery breaks silently. Session appears online but receives nothing. In the 2026-05-21 incident, jp master (janice-0) went silent for ~15h with the roster waiting.
     Without this call, you will NOT receive chat_send messages as they arrive — you'll only see them on your next user-prompted turn, making real-time coordination impossible.
     Your session_id is in the `🆔 khimaira session_id` block at the top of your context. Pass it to chat_my_chats every turn.
     After calling chat_my_chats: read recent chat history for a `📋 CONTEXT UPDATE v1` — that is your project context. If none exists, post a notice to intake asking master to post one. Do NOT begin implementation without it.

     CHANNEL REMINDER (now that real-time is active):
     `chat_send` → real-time delivery to all chat members. Use for anything time-sensitive.
     `session_post_notice` → turn-gated, lands on next prompted turn. Use for async FYIs only.
     Default: when in doubt, use `chat_send`.

     Question routing: route questions to INTAKE first (not master/Joseph, not silent). Intake resolves or escalates. Use `session_post_notice(target_session_id="<intake-name>", text="<question>")`.
     Standby.
     ```
   - Vary the "what you do" line to be role-specific (only the bullet for THIS role).

9. **Final summary in master's window** (three variants based on path taken):

   **New chat created (step 6 path):**
   ```
   ✅ Roster live: <chat_id> "<title>" (hierarchical, N members briefed)
     • master:    khimaira-0
     • intake:    intake-1
     • agent:     agent-1, agent-2, agent-3
     • observer:  observer-1
     • analyst:   analyst-1 (if present)
     • verifier:  verifier-1 (if present)
     • architect: architect-1
     • critic:    critic-1
   N pending acceptance: [<unaccepted names if any>]

   Next: type a request — intake-1 will receive it via the user-facing flow.
   (Or address master directly to bypass intake.)
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

- `/khimaira-spawn-architect` — spawn a single architect sidecar (architect-only flow)
- `/khimaira-spawn-intake` — spawn a single intake (intake-only flow)
- `/khimaira-assign` — once roster is live, delegate work to agents
- `/khimaira-consult` — once roster is live, consult the architect
- `/khimaira-deputize` — pause master + transfer role to a vice (separate from bootstrap)
