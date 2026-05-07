# Code Conventions

## General principles

- Code should be self-documenting through clear naming, but comments explain the _why_ behind non-obvious decisions.
- Every file should have a single, clear responsibility. If you can't describe what a file does in one sentence, it's doing too much.
- Follow the established patterns of the codebase you're in. Don't invent new patterns when existing ones work. If a pattern needs to change, change it everywhere — not just in your new code.

## Naming

- **Files:** Name must clearly reflect the functionality inside. No generic `utils.js` holding unrelated logic — name it `authHelpers.js`, `dateFormatters.js`, etc.
- **Variables & functions:** Descriptive and aligned with what they do. No single-letter variables outside loop counters and trivially obvious arrow function params. No generic `data`, `result`, `temp` unless scope is trivially small.
- **Consistency:** If existing code calls it `deliverableId`, don't introduce `delId` or `delivId`. Match existing patterns.
- **Boolean variables:** Should read as a question — `isLoading`, `hasPermission`, `canEdit`, `shouldRefetch`.
- **Functions:** Should describe the action — `fetchUserProfile`, `validateInput`, `transformResponse`. Event handlers: `handleClick`, `onSubmit`.

## Frontend conventions

- **Always camelCase.** All local variables, function names, parameters, destructured bindings. Only exceptions: React component names (PascalCase) and module-level true constants (SCREAMING_SNAKE_CASE).
- **Never use snake_case** in frontend code — except when constructing a POST/PUT/PATCH request payload that the backend expects in snake_case. Keep all local variables camelCase regardless.
- **ES6+ is mandatory.** Fat arrow functions for all callbacks and function expressions. `const`/`let` (never `var`). async/await over `.then()` chains. Optional chaining, nullish coalescing, template literals, destructuring — use them everywhere they apply.
- Format with **Prettier** after every change. Prettier does NOT add logical blank lines — that's the author's/AI's job.
- Add blank lines between logical phases in functions (validate → fetch → transform → return). One blank line before `return` in non-trivial functions. Split long async/effect bodies into named helpers.

## Backend conventions (Python)

- Follow PEP 8. Use type hints consistently. Prefer `pathlib` over `os.path`.
- Format with **Black** after every change.
- Docstrings on all public functions and classes.
- Use `async`/`await` for all I/O-bound operations. Never block the event loop.
- Group imports: stdlib → third-party → local, separated by blank lines.

## Folder structure

- **Never flat unless absolutely necessary.** Group files by feature or domain. Nest logically.
- If a folder has 8+ files, it needs subdirectories.
- Index files (`index.js`, `__init__.py`) should re-export or configure — not contain business logic.

## Comments

- Comment non-obvious logic, intent, and "why" (not just "what"). Keep comments brief and up to date.
- Use JSDoc/docstrings for public APIs and exported functions.
- Every file should have a brief header comment explaining its purpose if the filename alone isn't sufficient.
- Delete stale comments. A wrong comment is worse than no comment.

## Modularity

- Extract reusable logic into helpers, hooks, or utilities — but don't abstract prematurely. Three similar lines are better than a premature abstraction.
- Keep modules focused. If a file exceeds ~300 lines (backend) or ~250 lines (frontend component), consider splitting.
- Shared logic goes in shared directories. Feature-specific logic stays in the feature folder.

## Dead code

- **Delete dead code as soon as you confirm it's dead.** Don't leave unused functions, classes, files, imports, or branches in place "just in case." Don't comment them out. Don't add `# TODO: remove`. Just delete.
- **Verify before deleting.** Grep the entire repo for the symbol name. Check for string-based references (dynamic imports, getattr, registry lookups, config files, frontend selectors). If a function might be called by reflection or by a string, it's not dead — leave it and document the indirect caller.
- **Never add new code to a dead function.** If you find yourself editing a function with no callers, stop. Either the function is alive (find the real caller and verify your edit fits) or it's dead (delete it instead of building on top of it). Adding code to a dead function compounds the problem — the next reader has more to untangle.
- **Tests count as callers.** A function only used by tests for an unused feature is still dead — delete the tests with the function. A function used by tests that exercise a live feature is alive.
- **Git history is the safety net.** If you delete something and later need it, `git log -S 'symbolName'` finds the deletion commit. There's no need to keep dead code around for "version control" purposes — version control already does that.

## Markdown

- All markdown file names: **UPPERCASE** (e.g. `README.md`, `DESIGN.md`, `TODO.md`).
- Use **Mermaid diagrams** for data flows, state machines, sequence diagrams, architecture. Prefer Mermaid over ASCII art.
