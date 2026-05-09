# Global Claude Code Instructions

## Layout

Rules live in `~/.claude/rules/` (symlinked to `~/dotfiles/claude/rules/`) and are organized into two groups:

- **`rules/personal/`** — personal working style, not synced to Cursor
- **`rules/engineering/`** — team engineering standards, synced to Cursor as `.mdc` via `tool sync`

## MCP tooling suite

Five MCP servers available. Usage guides are embedded in each server's `FastMCP(instructions=...)` — Claude loads them automatically on connect. No rule files to maintain.

| Server | Purpose |
|---|---|
| **Chimera** | Multi-model orchestration + LangGraph monitor + multi-session shared state + process observability |
| **Séance** | Semantic code search via vector embeddings |
| **Specter** | Browser debugging via CDP (console, screenshots, React, interaction) |
| **Scarlet** | Codebase cartography (feature CLAUDE.md, barrels, dep graphs) |
| **Serena** | LSP-powered symbol navigation (jeevy_portal only) |

## Chimera session logging

Externalize meaningful state via the `mcp__chimera__session_*` tools so parallel Claude Code sessions can see what you're up to. File touches log themselves via the PostToolUse hook — these instructions cover the volitional acts.

**On the FIRST turn of every session:**

1. Identify your `session_id`: call `mcp__chimera__session_list()`. Pick the most-recently-active entry that has 0 decisions and recent file touches matching this conversation. That's you.
2. Name yourself: `mcp__chimera__session_set_name(session_id, "<slug>")` — kebab-case slug describing the work (e.g., `jeevy-auth-fix`, `chimera-monitor`). Other sessions can then refer to you by name instead of UUID.
3. Set initial status: `mcp__chimera__session_set_status(session_id, "researching", "<short detail>")`.

**Throughout the session:**

- After committing to an architectural choice, call `mcp__chimera__session_log_decision(session_id, text="<1-2 sentences>", why="<rationale>")`. Don't log trivial things ("rename foo to bar" is not a decision; "use Postgres read-only for safety" is). Aim for 3-8 decisions per substantive session.
- When something needs another session to research / answer, call `mcp__chimera__session_log_question(session_id, text="<question>")`. Returns a `question_id` — keep working, another session may answer.
- On status transitions, call `session_set_status(session_id, status, detail)` — values like `researching`, `implementing`, `blocked`, `awaiting-review`.

**On a new turn that finishes a non-trivial work block:**

Check `mcp__chimera__session_pending_notes(session_id)` for unread answers from other sessions. (The SessionStart hook auto-reads on session boot; this catches mid-session updates.)

**Skip when:** nothing was decided, nothing is open, nothing changed status. Empty logs are fine; noise logs are worse than no logs.

## Personal rules

| Rule file | Scope |
|---|---|
| `rules/personal/approach.md` | Working style, research-first, challenge bad ideas |
| `rules/personal/workflow.md` | Rule sync, formatting, research workflow |

## Engineering rules

| Rule file | Scope |
|---|---|
| `rules/engineering/conventions.md` | Naming, code style, folder structure |
| `rules/engineering/error-handling.md` | Error patterns, error envelope format |
| `rules/engineering/testing.md` | Coverage, determinism, what to test |
| `rules/engineering/security.md` | Secrets, input validation, OWASP |
| `rules/engineering/database.md` | Migrations, queries, naming, indexing |
| `rules/engineering/performance.md` | Frontend, backend, API, database |
| `rules/engineering/api-design.md` | REST conventions, versioning, pagination |
| `rules/engineering/dependencies.md` | Evaluation, pinning, auditing |
| `rules/engineering/debugging.md` | Process, anti-patterns, tools |
