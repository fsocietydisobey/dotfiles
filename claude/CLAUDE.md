# Global Claude Code Instructions

## Rules digest (read this first)

**`~/.claude/rules/DIGEST.md` is the load-bearing-principles version of every rule below.** When context is tight or the agent is mid-tool-call and can't re-load the full rule files, the digest is the fallback. It's auto-generated from each rule's `## TL;DR` section by `claude/rules/.generate-digest.sh`. If a principle in the digest applies, drill into the full rule for nuance.

## Layout

Rules live in `~/.claude/rules/` (symlinked to `~/dotfiles/claude/rules/`) and are organized into two groups:

- **`rules/personal/`** — personal working style, not synced to Cursor
- **`rules/engineering/`** — team engineering standards, synced to Cursor as `.mdc` via `tool sync`

Every rule file starts with a `## TL;DR` section. The digest concatenates them. See `personal/workflow.md` for the format convention.

## MCP tooling suite

Two MCP servers available (after NORTH_STAR Phase 0 / 2026-05-13 unification). Usage guides are embedded in each server's `FastMCP(instructions=...)` — Claude loads them automatically on connect.

| Server | Purpose |
|---|---|
| **Khimaira** | Unified surface — orchestration + LangGraph monitor + multi-session shared state + process observability + semantic code search (Séance, `seance_*` tools) + browser debugging via CDP (Specter, `specter_*` tools) + codebase cartography (Scarlet, `scarlet_*` tools) + meeting audio capture + transcription (Sibyl, `sibyl_*` tools). One MCP connection, ~119 tools. |
| **Serena** | LSP-powered symbol navigation (jeevy_portal only). Not part of the khimaira workspace. |

Séance, Specter, Scarlet, and Sibyl now ship inside the khimaira workspace at `packages/{seance,specter,scarlet,sibyl}/`. Their FastMCP tools are re-registered on khimaira's MCP server at boot under source-prefixed names. The legacy standalone `seance serve` / `specter serve` / `scarlet serve` / `sibyl serve` paths continue to work for backward compatibility — drop them from `claude mcp` once khimaira is registered.

## Khimaira session logging

Externalize meaningful state via the `mcp__khimaira__session_*` tools so parallel Claude Code sessions can see what you're up to. File touches log themselves via the PostToolUse hook — these instructions cover the volitional acts.

**On the FIRST turn of every session:**

1. Identify your `session_id`: call `mcp__khimaira__session_list()`. Pick the most-recently-active entry that has 0 decisions and recent file touches matching this conversation. That's you.
2. Name yourself: `mcp__khimaira__session_set_name(session_id, "<slug>")` — kebab-case slug describing the work (e.g., `jeevy-auth-fix`, `khimaira-monitor`). Other sessions can then refer to you by name instead of UUID.
3. Set initial status: `mcp__khimaira__session_set_status(session_id, "researching", "<short detail>")`.

**Throughout the session:**

- After committing to an architectural choice, call `mcp__khimaira__session_log_decision(session_id, text="<1-2 sentences>", why="<rationale>")`. Don't log trivial things ("rename foo to bar" is not a decision; "use Postgres read-only for safety" is). Aim for 3-8 decisions per substantive session.
- When something needs another session to research / answer, call `mcp__khimaira__session_log_question(session_id, text="<question>")`. Returns a `question_id` — keep working, another session may answer.
- On status transitions, call `session_set_status(session_id, status, detail)` — values like `researching`, `implementing`, `blocked`, `awaiting-review`.

**On a new turn that finishes a non-trivial work block:**

Check `mcp__khimaira__session_pending_notes(session_id)` for unread answers from other sessions. (The SessionStart hook auto-reads on session boot; this catches mid-session updates.)

**Skip when:** nothing was decided, nothing is open, nothing changed status. Empty logs are fine; noise logs are worse than no logs.

## The rules themselves

Every file in `rules/personal/` and `rules/engineering/` is auto-loaded, so their
full text is already in context — there is nothing here to look up. For the
one-line-per-rule version read `rules/DIGEST.md`, regenerated from their TL;DRs
by the pre-commit hook whenever a rule changes.

This section used to be two hand-maintained tables naming each file and its
scope. Removed 2026-07-29: they had drifted to listing 11 of 16 rules, silently
omitting `bug-class-enumeration`, `orchestration`, `khimaira-tools`,
`behavioral-rule-promotion` and `ai-engineering` — several of the most
load-bearing in the set. A stale index is worse than none: it reads as
authoritative and quietly says a rule does not exist. `ls rules/*/` and
DIGEST.md cannot drift that way.
