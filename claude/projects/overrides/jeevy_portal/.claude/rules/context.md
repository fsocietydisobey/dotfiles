# Context Loading & Architecture Map Sync

## Session startup (CRITICAL)

At the beginning of every session — before writing any code — read these files to build your mental model:

1. **`shared-docs/AI_CONTEXT.md`** — compressed knowledge base of everything built. This tells you the current state of each domain.
2. **The relevant architecture map(s)** for the domain you're about to work in (all maps live in `shared-docs/architecture/`):
   - Backend services: `shared-docs/architecture/BACKEND_SERVICES.md`
   - Backend API: `shared-docs/architecture/BACKEND_API.md`
   - Backend agents: `shared-docs/architecture/BACKEND_AGENTS.md`
   - Frontend features: `shared-docs/architecture/FRONTEND_FEATURES.md`
   - Frontend store/state: `shared-docs/architecture/FRONTEND_STORE.md`
   - Frontend shared: `shared-docs/architecture/FRONTEND_SHARED.md`

If the domain is unclear from the user's request, read `AI_CONTEXT.md` and the architecture map closest to the request. When in doubt, read more context — not less.

## Before editing any file

Before modifying a file, understand its neighborhood:
1. Read the file's imports — what does it depend on?
2. Check who imports it — `grep` for the filename across the codebase.
3. Read the architecture map for the layer it lives in.

This prevents breaking changes that ripple through the codebase.

### Special-case: editing under `backend/core/agents/`

The agent layer is governed by the **Subgraph Boundary Contract** — a layered import DAG enforced by `backend/scripts/lint_agent_imports.py`. Before adding or rewriting an `import` inside `backend/core/agents/`:

1. Identify the source layer of the file you're editing (`shared`, `orchestrator_root`, `subgraph:<name>`, `profile:<name>`, `profile_adapter`, or `shop`).
2. Identify the target layer of the import you want to add.
3. Check the rules in `shared-docs/architecture/BACKEND_AGENTS.md` § "Subgraph Boundary Contract" or `.claude/rules/agents.md` to confirm the edge is allowed.
4. If the edge is forbidden, do NOT route around the linter — the helper you want to import probably belongs in `_shared/` instead. Extract it.

Always run the linter before opening a PR:

```bash
source backend/.venv/bin/activate
python backend/scripts/lint_agent_imports.py
```

CI also runs it on every push (`.github/workflows/staging_tests.yml` Pytest CI workflow).

## Vague queries — the no-embeddings retrieval workflow

When the user asks about a topic without naming a specific file, symbol, or path — e.g. *"where's the rate limiting logic?"*, *"how does the auth flow work?"* — **never grep blindly**. Cursor solves this with vector embeddings; we deliberately don't have those (see `nvim-notes/AI-WORKFLOW.md` for why). Instead, work through these layers in order:

1. **`shared-docs/architecture/GLOSSARY.md`** — hand-curated concept-to-file mappings. Auto-loaded at session start. **Always check this first.** If the topic matches an entry, jump straight to those files. Don't burn tool calls searching when the answer is documented.

2. **The relevant architecture map** in `shared-docs/architecture/` — describes each domain at a high level. Tells you which directory to look in even when it doesn't name the exact file.

3. **Serena's `find_symbol`** — search for the topic with multiple casing variations (`rate limit`, `rateLimit`, `RateLimit`, `rate_limit`) and synonyms (`throttle`, `quota`, `limiter`).

4. **Serena's `search_for_pattern`** — regex search across the codebase with semantic filtering. Better than raw grep because it's symbol-aware.

5. **Glob common locations** based on topic category (middleware concepts → `backend/core/middleware/`, service concepts → `backend/core/services/`, frontend feature concepts → `frontend/src/features/`, etc.).

6. **Last resort: Grep with broad patterns.** By this point you should suspect the concept may not exist in the codebase yet.

**After answering a vague query**, if you found the answer through fallback search (steps 3-6), **suggest the user add the mapping to `GLOSSARY.md`** so future sessions skip the search. The glossary stays useful by accumulating successful searches.

There is also a `/find <topic>` slash command that runs this exact workflow — use it (or recommend the user invoke it) when the search needs to be especially thorough.

## Architecture map sync (CRITICAL)

The architecture maps in `shared-docs/architecture/` are living navigation indexes. They must stay accurate. When you make structural changes, update the relevant map in the same operation:

### What triggers a map update

- **Adding or removing a file** in any mapped directory (endpoints, services, features, store endpoints, shared components)
- **Adding or removing a feature folder** in `features/`
- **Adding or removing an RTK Query endpoint file** in `store/api/endpoints/`
- **Adding or removing a service** in `core/services/`
- **Adding or removing an API endpoint file** in `api/v1/endpoints/`
- **Changing a component's responsibility** (rename, merge, split)
- **Changing data flow patterns** (new SSE events, new cache invalidation tags, new context providers)
- **Adding or removing shared components, hooks, or contexts**

### Which map to update

| Change location | Update |
|----------------|--------|
| `backend/core/services/` | `shared-docs/architecture/BACKEND_SERVICES.md` |
| `backend/api/v1/endpoints/` | `shared-docs/architecture/BACKEND_API.md` |
| `backend/core/agents/` | `shared-docs/architecture/BACKEND_AGENTS.md` |
| `frontend/src/features/` | `shared-docs/architecture/FRONTEND_FEATURES.md` |
| `frontend/src/store/` | `shared-docs/architecture/FRONTEND_STORE.md` |
| `frontend/src/shared/` | `shared-docs/architecture/FRONTEND_SHARED.md` |

### How to update

- Keep entries concise — one line per file/component. These are indexes, not documentation.
- Preserve the existing table format. Add new rows, remove deleted rows, update changed descriptions.
- Do not add implementation details. The map says *what exists and where* — the code says *how it works*.

This is automatic — do not ask "should I update the map?" Just do it as part of the change.

## Post-session architecture update

When the user says **"update architecture maps"**, **"update architecture"**, or **"/update-architecture"**:

1. **Scan changes** — run `git diff --name-only HEAD~N` (or check the working tree) to identify all modified/added files in the session.
2. **Map each change** — for each changed file, identify which architecture map(s) it affects using the "Which map to update" table below.
3. **Read each affected map** — check if the changed files/components are already documented.
4. **Report drift** — list what's missing, outdated, or stale per map.
5. **Apply targeted updates** — edit only the sections affected by the changes. Don't regenerate from scratch — preserve existing content and patch.
6. **Update GLOSSARY.md** — add entries for any new concepts, patterns, or components introduced.

This is different from a full resync (which regenerates maps from directory scans). This command is for catching changes made during a specific session and ensuring they're reflected in the maps.

## Resync commands

When the user says **"resync architecture maps"**, **"rebuild architecture maps"**, or **"resync \<map-name\>"**: scan each mapped directory, read every file's purpose, and regenerate the map(s) in `shared-docs/architecture/` from scratch. Run directory scans in parallel. Don't preserve old content — overwrite with current state. See `shared-docs/architecture/COMMANDS.md` for full command reference.

When the user says **"audit architecture maps"**: read all maps and spot-check them against the codebase. Report drift but do NOT modify files.

## Architecture map files

All maps are centralized in `shared-docs/architecture/`:

```
shared-docs/architecture/
  INDEX.md                # Codebase tree + links to all maps
  COMMANDS.md             # Resync and audit commands reference
  BACKEND_SERVICES.md     # All 40+ services: domain, AI/processing, infrastructure
  BACKEND_API.md          # All 47 API endpoints, response patterns, auth
  BACKEND_AGENTS.md       # Agent graphs, subgraphs, tools, state, patterns
  FRONTEND_FEATURES.md    # All 23 feature modules, route mapping, key features deep-dive
  FRONTEND_STORE.md       # RTK store: base query chain, 28 endpoints, 4 slices, conventions
  FRONTEND_SHARED.md      # 60+ components, 17 contexts, 8 hooks, layouts, utils
```

## Context for Avante (in-editor AI)

When using Avante for complex work, manually load context before prompting:

```
/add shared-docs/AI_CONTEXT.md
/add shared-docs/architecture/<relevant-map>.md
/effort high
```

This compensates for Avante not having automatic codebase retrieval.
