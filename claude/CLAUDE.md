# Global Claude Code Instructions

## MCP tooling suite

Four MCP servers are registered globally. Usage instructions for each are in `~/.claude/rules/`:

| Server | Rule file | Purpose |
|---|---|---|
| **Séance** | `rules/seance.md` | Semantic code search via vector embeddings |
| **Specter** | `rules/specter.md` | Browser debugging via CDP (console, screenshots, React, interaction) |
| **Scarlet** | `rules/scarlet.md` | Codebase cartography (feature CLAUDE.md, barrels, dep graphs) |
| **Serena** | *(jeevy_portal only)* | LSP-powered symbol navigation |

## Engineering rules

General engineering rules are in `~/.claude/rules/`:

| Rule file | Scope |
|---|---|
| `approach.md` | Working style, research-first, challenge bad ideas |
| `conventions.md` | Naming, code style, folder structure |
| `workflow.md` | Rule sync, formatting, research workflow |
| `error-handling.md` | Error patterns, error envelope format |
| `testing.md` | Coverage, determinism, what to test |
| `security.md` | Secrets, input validation, OWASP |
| `database.md` | Migrations, queries, naming, indexing |
| `performance.md` | Frontend, backend, API, database |
| `api-design.md` | REST conventions, versioning, pagination |
| `dependencies.md` | Evaluation, pinning, auditing |
| `debugging.md` | Process, anti-patterns, tools |
