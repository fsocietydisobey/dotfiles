---
description: Migrations, query patterns, naming, indexing, data integrity
paths:
  - "**/migrations/**"
  - "**/models/**"
  - "**/*.sql"
  - "**/supabase/**"
  - "**/db/**"
  - "**/repositories/**"
  - "**/repository/**"
---

# Database

## TL;DR

Never edit existing migrations — create a new one. Parameterized queries only. snake_case tables/columns. Index WHERE/JOIN/ORDER BY columns. Foreign-key constraints + NOT NULL by default. Row-level security for multi-tenant.

## Migrations

- **Never edit existing migrations.** They may have already run in other environments. Create a new migration for every schema change.
- **One migration per feature.** Keep migrations focused and atomic. Don't bundle unrelated schema changes.
- Name migrations descriptively: `001_create_users_table.sql`, `002_add_email_verification.sql` — not `update.sql`.
- Test migrations both forward (up) and backward (down/rollback) when the platform supports it.

## Query patterns

- **Never put raw SQL in route handlers or controllers.** All database access goes through a repository or data access layer.
- Use parameterized queries exclusively. No string interpolation with user data. No exceptions.
- Prefer ORM/query-builder methods for standard CRUD. Use raw SQL only for complex queries that the ORM can't express cleanly — and isolate those in the repository layer.
- Watch for N+1 queries. If you're querying inside a loop, you probably need a JOIN or a batch fetch.

## Naming conventions

- Tables: **plural, snake_case** (`users`, `project_members`, `ingest_sources`).
- Columns: **snake_case** (`created_at`, `file_type`, `is_active`).
- Foreign keys: `<referenced_table_singular>_id` (e.g. `user_id`, `project_id`).
- Indexes: `idx_<table>_<columns>` (e.g. `idx_users_email`).
- Constraints: `fk_<table>_<referenced>`, `uq_<table>_<columns>`, `chk_<table>_<condition>`.

## Indexing

- Index columns used in WHERE, JOIN, and ORDER BY clauses.
- Don't index columns with low cardinality (e.g. boolean flags on small tables) — the planner won't use them.
- Composite indexes: put the most selective column first.
- Review query plans (`EXPLAIN ANALYZE`) for slow queries before adding indexes blindly.

## Security

- Enable Row-Level Security (RLS) on multi-tenant tables. Don't rely on application-layer filtering alone.
- Service accounts used by the backend should have minimum necessary permissions.
- Never store plaintext passwords. Use bcrypt, argon2, or equivalent.

## Data integrity

- Use foreign key constraints. Don't rely on application code to enforce referential integrity.
- Use `NOT NULL` by default. Only allow nulls when there's a clear semantic meaning for "no value."
- Use enums or check constraints for columns with a known set of valid values.
- Timestamps: always store in UTC. Convert to local time at the presentation layer.

## Local DB inspection

- If the project registers a Postgres (or equivalent) MCP query server, prefer its read-only query tool over `bash + curl + jq` plumbing for one-off DB inspection. A single tool call with structured results beats multi-line shell incantations and is auditable in the conversation.
- Schema introspection (table list, columns, types) is just SQL against `information_schema` — no separate tool needed.
- Local-DB MCPs can't reach staging/prod by design — their connection is bound at MCP registration time. For staging/prod inspection use the project's deployed dashboard or a service-role + curl path.
- Project-specific details (which MCP, which database, which connection string) live in the project's onboarding docs or `<repo>/.mcp.json` — not here.
