# Backend Rules (backend/)

## Python conventions

- Follow PEP 8 and Python best practices. Use type hints consistently. Prefer `pathlib` over `os.path`.
- **Format every file you touch with Black** — don't wait for commit time, format as you go:
  ```bash
  source /home/_3ntropy/work/jeevy_portal/backend/.venv/bin/activate && black <files>
  ```
- The backend venv lives at `backend/.venv/` (not `backend/venv/`). Activate it before any `python`, `pip`, `black`, or `pytest` command.
- Docstrings on all public functions and classes (Google style or numpy style — be consistent within a module).
- Use `async`/`await` for all I/O-bound operations. Never block the event loop with synchronous calls.

## FastAPI

- Routes under `api/v1/`. Return clear errors and use Pydantic for request/response.
- **No SQL in routes** — routes handle HTTP concerns only. All database queries go in the repository layer (`core/services/database/repositories/`).
- **All Pydantic models** (request/response schemas) go in `schemas/`, not inline in routes or services.
- For agent/streaming endpoints, return SSE or JSON consistently and handle "no state yet" without 500s (e.g. return empty history).
- Multi-line strings (prompts, docstrings): indent the string content with the enclosing block. Use `textwrap.dedent()` so the runtime value has no leading whitespace.

## Code organization

- **Layered architecture:** Routes → Services → Repositories → Models. Each layer only calls the one below it.
- Keep modules focused. If a file exceeds ~300 lines, consider splitting by responsibility.
- Group imports: stdlib → third-party → local, separated by blank lines (Black handles this with `isort`).
- **Agent layer (`backend/core/agents/`) has its own boundary contract** enforced by the DAG import linter (`backend/scripts/lint_agent_imports.py`). See `.claude/rules/agents.md` § "Subgraph Boundary Contract" before adding any import inside `core/agents/`. Do not route around the linter — extract shared helpers into `_shared/` instead.

## Supabase

- Enable RLS on new tables and add policies, or document why a table is backend-only.
