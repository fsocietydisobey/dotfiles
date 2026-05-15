# /khimaira-orchestrate <peer1,peer2,...> <scope description> — bootstrap a multi-turn collab chat

Spin up a chat with N peers, brief them with a templated kickoff, assign per-lane structured tasks, and stay available for review. The setup call for any work that needs more than a one-shot Q&A.

## Why this exists

Multi-turn collab work — doc co-authoring, multi-file refactors, design rounds — needs three primitives composed together: a *chat* (persistent transcript, can iterate), *tasks* (per-lane structured handoff with status), and a *templated brief* (so peers all start from the same prompt without copy-paste drift). This command bundles those three into a single setup call so the orchestrator agent doesn't have to remember the steps.

Distinct from:
- `/khimaira-delegate` — one-shot Q&A, returns answers, doesn't persist context.
- `/khimaira-chat` — creates the room but no briefing or task scaffolding.
- `/khimaira-chat-task` — one task to one peer; this command is the N-lane orchestration wrapper.

## When to use vs alternatives

| Need | Use |
|---|---|
| Multi-turn co-authoring / multi-stage work | `/khimaira-orchestrate` |
| One-shot parallel research → collect answers | `/khimaira-delegate` |
| Just open a chat, no task scaffolding | `/khimaira-chat` |
| Single peer, single bounded handoff | `/khimaira-chat-task` |
| Fully-specified mechanical batch | `/khimaira-swarm` |

## Args

```
/khimaira-orchestrate agent-1,agent-2 "phase-B docs: three-way authoring of khimaira-chat.md"
```

- First whitespace token = `peers_csv` (comma-separated session names or UUIDs).
- Everything after the first whitespace = `scope` (free-form description; becomes the chat title hint + brief preamble).
- If either piece is empty, render usage and stop.

## Steps

1. **Parse `$ARGUMENTS`**:
   - Split on first whitespace → `peers_csv`, `scope`.
   - Split `peers_csv` on commas, strip whitespace → list of peer names.
   - If either piece is empty, render `Usage: /khimaira-orchestrate <peer1,peer2,...> <scope description>` and stop.

2. **Resolve own session id** — from SessionStart hook context or `session_list()` fallback.

3. **Create the chat room** — call `mcp__khimaira-chat__chat_create_room(session_id=<my_id>, members=<peer list>, title=<truncated scope, ≤60 chars>)`. Capture `chat_id` from the response.

4. **Send the templated brief** — customize the template below by substituting `{scope}` and the lane summary, then call `mcp__khimaira-chat__chat_send(session_id=<my_id>, chat_id=<chat_id>, body=<filled brief>)`. The "ack with outline before drafting prose" gate is the load-bearing convention here — it's what prevents two peers shipping overlapping work.

5. **Create per-lane tasks** — for each peer, call `mcp__khimaira-chat__chat_task_create(session_id=<my_id>, chat_id=<chat_id>, body=<lane-specific scope>, assignee_session_id=<peer>)`. Capture each `task_id`. The lane scopes come from the orchestrator's understanding of the work — split the scope into N non-overlapping pieces before this step.

6. **Print the surface** — render:
   ```
   🌀 orchestration started: chat_id=<id>
   lanes: <peer1> → task-<...>, <peer2> → task-<...>, ...
   Stay available to triage outlines + approve final sections via chat_task_update.
   ```
   The closing line is the load-bearing reminder — orchestration without review is just delegation with extra steps.

## Templated brief (customize before sending)

```
🌀 ORCHESTRATION KICKOFF — {scope}

Lanes are assigned per-peer via chat_task_create (you'll see your task in chat).

For each peer:
1. Accept the chat invite (`/khimaira-chat-accept`).
2. Read your task's body for lane scope.
3. Reply with `## OUTLINE — <your lane>` (bullet form) BEFORE drafting full prose.
4. Wait for orchestrator greenlight on the outline.
5. Draft full prose, move your task to `done` via `chat_task_update`.
6. Orchestrator approves or requests changes — rework loops back to `in_progress`.

Cross-pollinate freely — peers should chat about lane boundaries before drafting if anything's ambiguous.
```

The orchestrator should edit `{scope}` and add any task-specific context (links, references, constraints) before sending. Don't copy verbatim — the template is a starting point, not a script.

## When NOT to use

- **Single peer, single task** → use `/khimaira-chat-task` directly. No need for the chat+brief+lanes scaffolding.
- **Fully-specified mechanical work** → use `/khimaira-swarm`. Orchestration adds review overhead that batch work doesn't need.
- **One-shot research questions** → use `/khimaira-delegate`. Returns answers without leaving a persistent chat behind.
- **The orchestrator can't actually stay available to review** → don't orchestrate. A delegated outline that no one approves is just an outline.

## Notes

- This command is *bootstrap*. After it runs, the normal chat (`chat_send`, `chat_task_update`, `chat_history`) and task tools drive everything else.
- The orchestrator role is implicit-from-creator (Phase B v1) — they're the only session that can approve / request changes on per-lane tasks. v2 may lift this to an explicit role field on room meta.
- Peers with auto-accept allowlists (`chat_auto_accept_from`) skip the handshake entirely; combine the two for friction-free orchestration of trusted agents.
- The chat persists after work completes. Use `/khimaira-chat-delete` (creator-only) to archive when truly done.
