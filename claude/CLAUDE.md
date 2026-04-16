# Global Claude Code Instructions

## Layout

Rules live in `~/.claude/rules/` (symlinked to `~/dotfiles/claude/rules/`) and are organized into three groups:

- **`rules/personal/`** — personal working style, not synced to Cursor
- **`rules/engineering/`** — team engineering standards, synced to Cursor as `.mdc` via `tool sync`
- **`rules/mcp/`** — usage guides for the MCP tooling suite (transitional; will migrate into server `instructions=` — see WORKSTATION_TOOLING.md Phase 7)

## MCP tooling suite

Four MCP servers available:

| Server | Rule file | Purpose |
|---|---|---|
| **Séance** | `rules/mcp/seance.md` | Semantic code search via vector embeddings |
| **Specter** | `rules/mcp/specter.md` | Browser debugging via CDP (console, screenshots, React, interaction) |
| **Scarlet** | `rules/mcp/scarlet.md` | Codebase cartography (feature CLAUDE.md, barrels, dep graphs) |
| **Serena** | *(jeevy_portal only)* | LSP-powered symbol navigation |

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
