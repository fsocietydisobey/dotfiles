# /khimaira-transfer-session <new-session-name> — full context handoff to a fresh session

When this session's context window gets noisy/bloated but the work isn't done, this command packages every load-bearing piece of state — open tasks, recent decisions, in-flight work, scheduled wakeups, sister-session activity, project context, **AND active chat memberships with sister agents** — and hands it to whatever new Claude Code session boots next in the current cwd.

**The user types one command. Everything else is automatic:**

1. Donor (this session) gathers context + posts a structured handoff scoped to cwd
2. Donor updates its status to `transferred-out` and stays passively listening
3. User opens a fresh Claude Code window in the same project
4. The new session's SessionStart hook auto-surfaces the handoff
5. New session reads the context block, names itself `<new-session-name>`, asks follow-ups only if needed
6. Donor answers follow-ups (its UserPromptSubmit hook surfaces each one on next turn)
7. New session signals `transfer complete`
8. **Donor auto-transfers all active chat memberships to the recipient** (Phase B v1.2 — see step 8 below). Sister agents see `📦 transferred to <recipient>` channel blocks; recipient picks up every conversation transparently
9. Donor stands down

## Steps for the donor (this session)

### 1. Parse `$ARGUMENTS`

The full argument is the new session name (kebab-case slug recommended, e.g. `khimaira-7`, `pypi-watcher`, `task-66-followup`). If empty: render usage:

```
Usage: /khimaira-transfer-session <new-session-name>

Example: /khimaira-transfer-session khimaira-7

The new name is what the recipient will call itself. Choose
something descriptive so future cross-session references are
readable.
```

### 2. Gather donor state (parallel batch — ~6 tool calls)

Fire all of these in one message:

- `mcp__khimaira__session_state(session_id=<my-id>, recent=20)` — recent decisions, file touches, status
- `mcp__khimaira__session_list()` — what other sessions exist + their statuses
- `mcp__khimaira__list_tasks(hook_safe_only=false)` — open tasks from task sources
- `mcp__khimaira__session_consume_handoffs(session_id=<my-id>, cwd=<cwd>)` — any pending project handoffs
- `Bash: git log --oneline -10 && git status --short && pwd` — project state
- `Bash: ls <cwd>/tasks/ 2>/dev/null` — in-tree task specs

### 3. Compose the handoff body

**Before composing**: note your own model + thinking-mode budget. The model is visible in your SessionStart hook context block (e.g. `Opus 4.7 (1M context)`); a default thinking-mode (if Joseph set one) is in `~/.claude/settings.json`. This populates the budget step in the template below so the recipient can choose to match the donor's tier or deliberately diverge.

Use this template **verbatim** (fill in the bracketed sections from gathered data + your own knowledge of what's in flight in this conversation):

```markdown
📦 **SESSION TRANSFER** from `<donor-name>` (id `<donor-id-8char>`)

This is a SESSION TRANSFER, not a generic task handoff. The previous session's
context window got noisy; the user wants you to pick up with a clean slate.
You're inheriting LOADED MENTAL MODEL + ACTIVE WORK — read everything below.

## Step 1 — claim your identity

First thing on your first turn, call:

    mcp__khimaira__session_set_name(
        session_id="<your-session-id>",
        name="<new-session-name>"
    )

`<new-session-name>` is what the user asked for. Your session_id is in
your SessionStart hook output.

Then:

    mcp__khimaira__session_set_status(
        session_id="<your-session-id>",
        status="implementing",  # or whatever fits the in-flight work below
        detail="taking over from <donor-name>"
    )

## Step 2 — recommended budget for continuity

Donor's budget at handoff time: <DONOR FILLS IN: model from SessionStart hook + any non-default thinking-mode from settings.json, e.g. "Opus 4.7 + ultrathink">

Recipient inherits master role via `chat_transfer_membership` (Phase B v2, single-master invariant per `tasks/khimaira-chat/PHASE-B-V2-ROLES-AUDIT.md`). Default budget per role (see `docs/khimaira-chat.md#token-cost-budgeting` for rationale + when-to-deviate):

| Role     | Model       | Thinking                  |
|----------|-------------|---------------------------|
| Master   | Opus 4.7    | ultrathink / think harder |
| Agent    | Sonnet 4.6  | think (short budget)      |
| Observer | Haiku 4.5   | default / none            |

You inherit `master` — run Opus 4.7 + ultrathink unless Joseph asks otherwise. When you spawn subordinate agents/observers in your own orchestration rounds, route them to their tier per the table above to avoid the rate-limit blowup that motivated v1.4.

## Step 3 — read the context (no questions yet)

Read this whole handoff carefully. Most of what you need to know is here.
Ask follow-ups via `session_log_question(target=<donor-id>)` ONLY if
something is genuinely unclear after you've read the whole block.

Donor is listening but every back-and-forth costs the user a context switch.

## Step 4 — project + cwd

Working directory: <cwd>

Recent commits (HEAD ← 10):
<paste output of `git log --oneline -10`>

Working tree state:
<paste output of `git status --short` — note any untracked or modified files>

## Step 5 — recent decisions on this session (last 20)

<paste session_state's recent_decisions block — each with text + why>

## Step 6 — active work mid-stream

<DONOR FREE-FORM PROSE — this is the most important section. Write what
you (the donor) are CURRENTLY in the middle of. Include:
  - What you just shipped (last 3-5 commits or actions)
  - What you're partway through (uncommitted work? half-finished phase?)
  - What's queued next that you haven't started
  - Any tricky context the recipient won't pick up from session_state alone
    (e.g. "the user said X mid-conversation that changed the plan")
Write this in 3-7 paragraphs. The recipient reads this once; make it count.>

## Step 7 — scheduled wakeups (donor's responsibility, FYI)

<List any ScheduleWakeup the donor has pending. Note: wakeups fire in
the donor's process, NOT the recipient's. The donor handles residuals.
If results matter to the recipient, donor will notice + relay.>

Example shape:
- ⏰ PyPI sibling publish cascade — donor wakeup at <iso-time>; will retry
  publishes + notify recipient on success
- ⏰ <other wakeup if any>

## Step 8 — sister sessions active

<paste session_list output, filtered to last-active < 60min, with one-line
descriptions of what each is doing if known>

## Step 9 — open tasks

External task sources (Linear / GitHub / JSONL):
<paste list_tasks output>

In-tree specs (tasks/ dir):
<list of tasks/<name>/IMPLEMENTATION.md most-recently modified, with one-line each>

## Step 10 — pending handoffs in this cwd

<paste consume_handoffs output, or "none">

## Step 11 — signal transfer complete

When you've read everything above + are ready to take over (or you've
asked + received answers to your follow-ups), signal the donor:

    mcp__khimaira__session_post_notice(
        target_session_id="<donor-id-full-uuid>",
        text="✅ transfer complete — taking over from here. <optional note>",
        from_session_id="<your-session-id>"
    )

After that, the donor:
1. Stands down on the active work (status flips to `idle` or `transferred-out`).
2. **Auto-transfers all of its active chat memberships to you** (Phase B v1.2). On your NEXT turn, you'll see one `📦 <donor-name> transferred this chat to <your-name> — full context handoff` channel block per inherited chat. Sister agents in those chats see the same block and update their understanding of who they're talking to. You can read full transcripts via `chat_history(chat_id, your_session_id)` — the JSONL persists across the transfer.

You own the work from then on.

If you need to pull the donor back later (e.g. it had specific knowledge
about something you didn't realize you needed), `session_log_question`
still works — the donor session stays alive, just inactive.

If you don't want to inherit a particular chat (e.g. it's no longer relevant), call `chat_leave(chat_id)` on it — leaving any inherited chat is harmless and doesn't affect the others.

---

You have the same MCP toolkit, the same Claude Code keybinds, the same
codebase. The only thing fresh is your context window. Make it count.

— <donor-name> (signing off after transfer complete)
```

### 4. Post the handoff

Call `mcp__khimaira__session_post_handoff` with:

- `from_session_id=<my-id>`
- `text=<the composed body from step 3>`
- `scope_cwd=<git project root, NOT literal cwd>` — compute via `Bash: git rev-parse --show-toplevel`. If not in a git repo, fall back to `os.getcwd()`. **Why git-root, not literal cwd**: the daemon's handoff matching is "handoff.scope_cwd must be a prefix of new session's cwd" — if the donor was in `/repo/frontend/` and posted with the literal cwd, a recipient opening Claude Code in `/repo/` (parent) wouldn't see the handoff because `/repo/frontend` is not a prefix of `/repo`. Scoping to git-root makes the handoff visible to ANY new session opened anywhere within the repo, which is what users actually expect.
- `expires_in_hours=24`

24h TTL — transfers are short-lived. If the user doesn't open a new session within a day, the handoff expires and they re-run the command.

### 5. Update donor status

```python
mcp__khimaira__session_set_status(
    session_id=<my-id>,
    status="awaiting-transfer-recipient",
    detail="transfer queued for next session named <new-session-name>"
)
```

### 6. Log a decision (for the audit trail)

```python
mcp__khimaira__session_log_decision(
    session_id=<my-id>,
    text=f"Initiated session transfer to <new-session-name>. Donor stays passively listening; recipient signals complete when oriented.",
    why="Donor's context window got noisy/bloated; transferring active work to a fresh session per user request via /khimaira-transfer-session."
)
```

### 7. Print user-facing summary

```
📦 Transfer queued.

  Donor session : <donor-name> (this window)
  New session   : <new-session-name>
  Handoff id    : <handoff-id-8char>
  Scoped to     : <cwd>
  Expires in    : 24h

Next steps (automatic from here — you just open a new window):

  1. Open a fresh Claude Code session in <cwd>
  2. The handoff auto-surfaces via SessionStart hook
  3. New session reads context, claims name, asks any follow-ups
  4. When you see "✅ transferred" surface here, donor is done

Donor stays passively listening — type anything in this window
to check inbox for incoming questions. Otherwise, donor handles
residual scheduled work (e.g. queued wakeups) and stands down
when the recipient signals complete.
```

## Notes on the donor → recipient protocol

- **Wakeups stay with donor.** The recipient inherits LOGICAL work but not scheduled events. If donor has a ScheduleWakeup pending (e.g. PyPI cascade), the wakeup fires in donor regardless of transfer. Donor handles + notifies recipient.

- **Donor stays alive.** Transferring is a soft passing of active work, not session destruction. Donor remains addressable by name + can answer follow-ups indefinitely.

- **Multi-round follow-ups are expected.** A complex transfer might involve 3-5 follow-up asks before the recipient is oriented. That's fine — each is one round trip via `session_log_question` + `session_post_answer`.

- **The handoff body is the contract.** Anything not in the handoff is information the recipient might miss. Err on the side of more detail in the "active work mid-stream" prose (step 6 of the template). It's the highest-leverage section.

- **Composes existing primitives + one Phase B v1.2 addition.** Uses `session_post_handoff` + `session_log_question` + `session_post_answer` + `session_post_notice` + `session_set_name` + `session_set_status` + `session_log_decision` for the session-level handoff; **plus `chat_transfer_membership` (Phase B v1.2) for the chat-membership transfer step that fires after the recipient signals complete**. The chat transfer is the only new primitive — everything else is existing.

## Edge cases

- **User opens new session in a different cwd OR a parent dir of the donor's cwd**: as of the git-root-scoping fix in step 4, this works transparently — anywhere within the same git repo is fine. If the new session is opened OUTSIDE the donor's git repo, the handoff still won't surface; user must open in the project tree OR run `/handoffs` manually pointing at the project root.

- **Multiple parallel transfers**: each gets its own handoff id; the new session sees ALL pending handoffs on boot. Disambiguate by name in the handoff body.

- **User abandons the transfer**: 24h TTL expires the handoff. Donor's `awaiting-transfer-recipient` status can be reset manually via `session_set_status` if the user wants to use donor again normally.

- **Recipient is confused even after follow-ups**: the user can always abandon the transfer + start fresh, or have the recipient run `/khimaira-orient` for a structural re-scan independent of the donor's prose.

## When NOT to use

- **Short sessions**: if the session has only been going for an hour with light context, just open a new window and let SessionStart's normal handoff/inbox surfacing carry forward what's needed. Transfer is for context-heavy multi-hour sessions.

- **End-of-task wrap-up**: if you're DONE with the work, don't transfer — just commit/push and close the session. Use `session_post_handoff` directly (or `/handoff <project>`) to leave a forward-looking note for tomorrow's session.

- **Active-only-to-myself work**: if the work is just "Joseph in chat with one agent," transferring to a new agent loses the rapport built in this conversation. Only transfer when the work is genuinely shareable / hand-offable.
