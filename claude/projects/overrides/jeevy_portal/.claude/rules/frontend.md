# Frontend Rules (frontend/)

## Code style

- **ES6+ is mandatory.** Fat arrow functions for all callbacks and function expressions. `const`/`let` (never `var`). async/await over `.then()` chains. Optional chaining, nullish coalescing, template literals, destructuring — use them everywhere they apply.
- **Always camelCase.** All local variables, function names, parameters, and destructured bindings must use camelCase. Only exceptions: React component names (PascalCase) and module-level true constants (SCREAMING_SNAKE_CASE).
- **Never use snake_case in frontend code** — except when constructing a POST/PUT/PATCH request payload that the backend expects in snake_case. Even then, build the payload object at the call site with snake_case keys, but keep all local variables camelCase.
- **Response property access: always camelCase.** `fastApiBaseQuery` auto-converts API responses from snake_case to camelCase. Always access response properties using camelCase (e.g. `source.fileType`, not `source.file_type`). Exceptions: SSE/streaming responses via raw `fetch()` (which bypass the converter) and data from legacy Next.js proxy routes (`app/api/`).

## Formatting & spacing

- **Format every file you touch with Prettier** — don't wait for commit time, format as you go:
  ```bash
  PATH="/home/_3ntropy/.nvm/versions/node/v22.13.0/bin:$PATH" && cd /home/_3ntropy/work/jeevy_portal/frontend && npx prettier --write src/path/to/file.js
  ```
- **Prettier does NOT add logical blank lines** between steps inside functions — that's the author's/AI's job. You must actively maintain readable spacing:
  - One blank line between logical phases inside a function (e.g. validate → fetch → transform → return).
  - One blank line before `return` statements in non-trivial functions.
  - One blank line between hook calls and the first logic block in React components.
  - Split long `async` / effect bodies with named helpers rather than letting them grow past ~30 lines.
  - Put repeated flows in `shared/utils` or feature-level helpers.
- When editing a file, **improve spacing and structure in the areas you touch** — don't leave dense walls of code behind you.

## RTK Query — Direct FastAPI Calls

- All new RTK Query endpoints must call FastAPI directly — do not create Next.js API proxy routes (`app/api/`).
- Add every new endpoint name to `FASTAPI_ENDPOINTS` in `store/api/rootApi.js` so `conditionalBaseQuery` routes it through `fastApiBaseQuery`.
- Endpoint URLs are relative to `/api/v1` (e.g. `url: 'projects/${id}'` resolves to `NEXT_PUBLIC_BACKEND_API_URL/api/v1/projects/{id}`).
- Auth is automatic: `credentials: 'include'` sends the `wos_session` cookie — no Bearer token header needed.
- Case conversion is automatic: request body → snake_case, response → camelCase (handled by `fastApiBaseQuery`).
- For SSE/streaming endpoints that can't use RTK Query: use raw `fetch()` with `credentials: 'include'` pointing to `NEXT_PUBLIC_BACKEND_API_URL/api/v1/...`.
- The Next.js proxy pattern (`app/api/` routes + `proxyToBackend`) is deprecated and being removed.

## Styling & structure

- Prefer RTK Query in `src/store/api/endpoints/` for data and mutations.
- Follow styling guides in `frontend/study-guides/styling/` (THEME_SYSTEM.md, responsive_and_styling_rules.md, ADDING_THEMES.md). Use existing CSS modules and Jeevy theme.
- Deliverable entity is the deliverable UUID (not quote or project id). Resolve via `getDeliverableByQuoteId` / `getDeliverableByProjectId` and pass `entityId` to the AI panel.

## Documentation as you go (organic growth, no sweeps)

These rules exist so documentation coverage grows through normal editing instead of one-shot rewrites. **Only apply to files you're already touching for another reason** — don't open files just to add docs.

### JSDoc `@description` on exported components and hooks

- **When you touch an exported component or hook, add a JSDoc `@description` if one is missing.** One sentence is enough. The goal is that every public surface has a brief contract statement that flows into IntelliSense and into embeddings for semantic search.
- Example (synthetic — not tied to any specific component):
  ```js
  /**
   * @description Renders a paginated list of items with selection and a delete affordance.
   * Data comes in via `items`; selection state is controlled by the parent.
   */
  export default function ItemList({ items, selectedId, onSelect, onDelete }) { ... }
  ```
- Keep it to one or two sentences. If you need more, the component probably belongs in the feature's `CLAUDE.md` gotchas section, not in JSDoc.
- If the file already has a JSDoc block, **leave it alone unless it's "wrong"**. "Wrong" means: the function signature has changed and the doc doesn't reflect it; the described behavior is no longer accurate; or the doc references a deprecated pattern. **Stale-but-correct** docs are fine — don't rewrite them just because they could be more elegant.

### Test names should read as behavior specifications

- **When you touch a test file (`<Component>.test.js`, `<module>.test.js`, or any `*.test.{js,jsx,ts,tsx}`), rewrite any generic test names you see into behavior spec form.** Test names are free documentation and rank well in semantic search.
- Bad: `it('test1')`, `it('works correctly')`, `it('handles input')`.
- Good: `it('shows a skeleton while drawings are loading')`, `it('displays an empty state when no drawings match the filter')`, `it('disables the submit button until all required fields are filled')`.
- Rule of thumb: the name should describe what a user or caller observes, not what the implementation does internally.
- This is a touching rule, not a sweep — don't open test files just to rename. Do it as you work.

## Feature-level CLAUDE.md files

Each folder under `frontend/src/features/<feature>/` has its own `CLAUDE.md` with feature-scoped vocabulary, public API, conventions, consumers, and gotchas. Claude Code auto-loads the one closest to the file you're editing, so no manual linking is needed.

- **When you change a feature's public API** (add/remove exports from `index.js`, rename a component, change a hook signature), update that feature's `CLAUDE.md` in the same change.
- **When you discover a new gotcha** (a non-obvious invariant, a deprecated pattern, a subtle race condition), add it to the feature's `CLAUDE.md` under "Known issues and gotchas".
- **When you add a new consumer** (a cross-feature import from another folder), update both features' `CLAUDE.md` files to reflect the new coupling.
- These files are living docs, not one-time snapshots — keep them accurate as part of normal editing.
