---
description: Review staged changes for bugs, performance, security, and convention adherence
---

Review the currently staged git changes against this project's standards.

## What to check

**Correctness**
- Logic bugs, off-by-one errors, race conditions, null/undefined handling
- Missing error handling at layer boundaries (routes, services, repositories)
- Unvalidated input crossing system boundaries
- Silent exception swallowing (catch blocks with no logging or re-raise)

**Performance**
- N+1 queries (database calls inside loops)
- Sync I/O in async code paths
- Missing pagination on list endpoints
- Unbounded result sets
- Missing indexes on new WHERE/JOIN/ORDER BY columns

**Security**
- Secrets in code, logs, or error messages
- Missing tenant scoping on queries (cross-tenant data leakage risk)
- Raw SQL string interpolation with user input
- Missing auth/permission checks on new endpoints
- PII logged at INFO level or above

**Architecture adherence**
- Routes containing business logic (should delegate to services)
- Services touching HTTP or raw DB (should go through repositories)
- Inner layers importing from outer layers (violates dependency direction)
- New top-level `utils/` folders (banned — use feature-scoped or `shared/`)
- Files exceeding size budgets (~300 lines backend, ~250 lines frontend components)
- **Agent layer Subgraph Boundary Contract** (when the diff touches `backend/core/agents/`):
  - Run `python backend/scripts/lint_agent_imports.py` locally if not already run — CI runs it on every push, but local-fail-first is faster than waiting for CI.
  - Watch for cross-subgraph imports (`subgraph:digestion → subgraph:ingest`, etc.), shop ↔ deliverable-family imports, and profile-to-profile imports — all forbidden by the DAG. The linter catches these but flag them in review too so the author understands the structural constraint.
  - Watch for shared helpers being added inside a specific subgraph (`nodes/digestion/common.py`, `tools/conversation/error_handler.py`) when they're generic enough to belong in `_shared/`. The cleanest fix to a forbidden import is usually "extract to `_shared/`", not "add an exception".
  - If the diff touches `backend/scripts/lint_agent_imports.py` (`ALLOWED_EDGES`, `classify()`, layer definitions), confirm the matching docs were updated: `shared-docs/architecture/BACKEND_AGENTS.md` § "Subgraph Boundary Contract", `.claude/rules/agents.md`, `.cursor/rules/langgraph.mdc`, and `CLAUDE.md` § "LangGraph / Agents". The linter is canonical, but those docs must stay in sync.
  - If the diff moves or renames a file in `core/agents/` that the worker imports (anything reachable from `workers/job_worker.py`), confirm the worker restart contract is acknowledged in the PR description. See `backend/workers/job_worker.py` module docstring.

**Conventions**
- Python not formatted with black
- Frontend not formatted with prettier
- snake_case leaking into frontend code (except POST bodies to backend)
- Missing type hints on Python signatures
- `any` used in TypeScript without justification

**Testing**
- New features without tests
- Bug fixes without a regression test
- Tests that mock the database layer (should use real containerized DB)

## How to report

Group findings by severity:

1. **Must fix** — bugs, security issues, convention violations
2. **Should fix** — performance concerns, missing tests, maintainability issues
3. **Worth knowing** — style nits, minor improvements, observations for future work

For each finding, cite the file path and line number. Explain *why* it matters — don't just quote the rule. If you'd do it differently, show the better version.

Reference `.claude/rules/` files for specifics when flagging convention violations.

Start by running `git diff --staged` to see what's being reviewed.
