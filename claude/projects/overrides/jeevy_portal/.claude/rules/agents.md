# LangGraph / Agents (backend/core/agents/, core/ai/)

## Architecture

- AI infrastructure lives in `core/ai/` (models, checkpointer, graph factory). Agent definitions live in `core/agents/` (graph, tools, state per domain).
- Tools that need a service are bound with `_bind_tools_with_svc()` so the agent doesn't need configurable injection.
- Middleware must implement both `wrap_tool_call` and `awrap_tool_call` when using `ainvoke()`/`astream()`.

### Agent layer structure

```
backend/core/agents/
  _shared/        # Cross-agent shared infra (tool binding, agent profile, tool errors, run events).
                  # Allowed to import only from core/ai/. Nothing else inside core/agents/.
  shop/           # Fully isolated shop agent (Gmail-driven). Has its own graph, state, prompts,
                  # nodes/, and tools/. ZERO overlap with the deliverable family.
  graphs/         # Deliverable-family graph topology (orchestrator, conversation, ingest, digestion, output).
  nodes/          # Deliverable-family node functions, grouped by subgraph.
  state/          # Deliverable-family state TypedDicts (DeliverableState lives in state/orchestrator.py).
  tools/          # Deliverable-family tools, grouped by subgraph.
  prompts/        # Deliverable-family system prompts.
  config/         # YAML configs + loaders. Note: tooling_profile.py and output_plan_adjustment.py
                  # are `profile_adapter` files (see Boundary Contract below).
  profiles/       # Agent variants: estimator/, project_manager/.
```

## Graph patterns

- Use `create_agent()` from `langchain.agents` for ReAct agents — pass `checkpointer=` directly.
- Use `StateGraph` from `langgraph.graph` for custom graphs — call `.compile(checkpointer=)`.
- For Supabase connections with `AsyncPostgresSaver`, use `prepare_threshold=0` in psycopg3 kwargs.
- Streaming: use `astream(stream_mode=["messages", "updates"])` yielding `(mode, data)` tuples. Inline the serialization.

## Subgraph Boundary Contract

The agent layer enforces a layered dependency rule. Code in one layer may only import from the layers it is allowed to depend on. Violations are caught by `backend/scripts/lint_agent_imports.py` (CI gate).

> **Canonical authority:** If this section conflicts with `backend/scripts/lint_agent_imports.py`, the linter is correct.

**Layers:**

- `_shared` — `core/agents/_shared/*` (cross-agent shared infra: tool binding, agent profile resolution, generic tool-error formatting, run-timeline event emission).
- `orchestrator_root` — `core/agents/graphs/orchestrator.py`, `nodes/orchestrator/*`, `state/orchestrator.py` (the top-level deliverable orchestrator and `DeliverableState`).
- `subgraph:<name>` for `name ∈ {conversation, ingest, digestion, output}` — the subgraph's graph file, nodes, state, tools, prompts, and any subgraph-specific config.
- `profile:<name>` for `name ∈ {estimator, project_manager}` — agent variants in `profiles/<name>/` and the prompt builder in `prompts/<name>.py`.
- `profile_adapter` — `config/tooling_profile.py` and `config/output_plan_adjustment.py`. Profile-aware dispatchers that sit between subgraphs and profiles.
- `shop` — `core/agents/shop/*` (a fully isolated agent — Gmail-driven, separate lifecycle).

**Rules:**

1. `_shared` may import only from `core/ai/`. Nothing else.
2. `orchestrator_root` may import from `_shared`, `core/ai/`, and any `subgraph:<X>` (it wires them as nodes). It may **NOT** import from `profile:<X>` (the base must not know about its profile overrides).
3. Each `subgraph:<X>` may import from `_shared`, `core/ai/`, and `orchestrator_root` (to extend `DeliverableState`). It may **NOT** import from any other `subgraph:<Y>` where `Y ≠ X`. Additionally, `subgraph:digestion` and `subgraph:output` may import their respective `profile_adapter` files.
4. Each `profile:<X>` may import from `_shared`, `core/ai/`, `orchestrator_root`, and any `subgraph:<Y>`. It may **NOT** import from any other `profile:<Y>` where `Y ≠ X`.
5. `profile_adapter` files may import from `_shared`, `core/ai/`, `subgraph:digestion`, `subgraph:output`, and the two profiles. They are the only files allowed to bridge subgraph and profile layers.
6. `shop` may import from `_shared` and `core/ai/`. It may **NOT** import from any deliverable-family code, and no deliverable-family code may import from `shop`.
7. **Lanes are control-flow only.** `nodes/orchestrator/lanes.py` must not read subgraph-internal state fields. (Socially enforced — the linter sees imports, not state-field accesses.)

**Why these rules matter:** The layer-first layout (`graphs/`, `nodes/`, `state/`, …) does not encode subgraph boundaries in the filesystem. Without the linter, a developer adding a new node to `nodes/digestion/` could trivially `from core.agents.nodes.ingest.pipeline import …` without any structural friction. The linter is the only structural guard against subgraph entanglement.

**Run the linter before opening a PR:**

```bash
source backend/.venv/bin/activate
python backend/scripts/lint_agent_imports.py
```

CI runs it automatically on every push.

## Source of truth

- **Read the actual code** in `core/agents/` and `core/ai/` — not the docs. Do NOT reference `docs/ingest-digest-ai/architecture/` for implementation details (those are historical design docs and may be outdated).
- See `shared-docs/architecture/BACKEND_AGENTS.md` for the architecture map.

## Maintaining docs (CRITICAL)

When you change the structure of `core/agents/` or `core/ai/` (add/remove/rename files, add a new agent, change graph flow, add a new model, add/remove/rename tools, change routing logic, add/modify subgraphs, **change the linter `ALLOWED_EDGES` or `classify()` table**), you **MUST** update:

1. **`shared-docs/architecture/BACKEND_AGENTS.md`** — Architecture map. Update directory structure, patterns, models table, AND the Subgraph Boundary Contract section if you touched the linter.
2. **`.claude/rules/agents.md`** AND **`.cursor/rules/langgraph.mdc`** — keep the Boundary Contract section here in sync if it changes (rule sync is CRITICAL).
3. **`CLAUDE.md`** (project root) — has the same Boundary Contract summary in its LangGraph section; keep in sync.
4. **`shared-docs/sources/langgraph-deliverable-agent/`** — Study guide. Update the relevant file(s): `ARCHITECTURE.md`, `STATE_AND_CHECKPOINTING.md`, `TOOLS.md`, `PROMPTS_AND_CONTEXT.md`, `INGEST_SUBGRAPH.md`, `SERVICES_AND_DATA.md`, `STREAMING_AND_API.md`.

This is automatic — do not ask "should I update the docs?" Just do it.

## Adding a new LangGraph node — signature gotcha

When adding a new node function to `core/agents/nodes/<subgraph>/`, two valid signature patterns exist:

```python
# Pattern A — required config (no default)
async def my_node(state: SomeState, config: RunnableConfig) -> dict:
    ...

# Pattern B — optional config (default None)
async def my_node(state: SomeState, config: RunnableConfig | None = None) -> dict:
    ...
```

**Critical:** Do NOT use `from __future__ import annotations` in a node file IF the node uses Pattern B. PEP 563 makes the type annotation a string (`'RunnableConfig | None'`), LangGraph's signature inspection fails on the string and silently passes `config=None` to the node — your `_db_service(config)` returns `None`, your DB writes silently no-op, and the only signal is a misleading warning where "should be" and "got" look identical. The graph still pauses correctly so this bug presents as "the node ran but nothing happened in the DB."

Either drop `from __future__ import annotations` (preferred — most digestion node files don't use it) or switch to Pattern A. See `shared-docs/joseph/notes/REVIEW_GATE_FUTURE_ANNOTATIONS_BUG.md` for the full discovery + the AST-based regression guard at `tests/unit/test_review_gate.py::test_review_gate_module_does_not_use_future_annotations`. Full pattern documentation lives in `shared-docs/architecture/BACKEND_AGENTS.md` § "Adding a New LangGraph Node".

## Worker restart contract

`backend/workers/job_worker.py` imports compiled LangGraph graphs at startup. When a deploy changes graph import paths or top-level structure (e.g. moving a graph file, changing `add_node()` string keys), worker processes loaded against the old paths will crash on next graph lookup. After such a deploy: drain queue → restart workers → unpause → monitor logs for `ImportError` for 30 minutes. Full procedure in `backend/workers/job_worker.py` module docstring.
