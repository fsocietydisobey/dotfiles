---
description: Scan recent changes and update architecture maps to reflect what was built
---

Update the architecture maps in `shared-docs/architecture/` to reflect changes made in the current session or recent commits.

## Steps

1. **Identify changes** — run `git diff --name-only HEAD~5` (or check working tree with `git status`) to find all modified/added/deleted files.

2. **Map changes to architecture files** — for each changed file, determine which map(s) are affected:
   - `backend/core/services/` → `BACKEND_SERVICES.md`
   - `backend/api/v1/endpoints/` → `BACKEND_API.md`
   - `backend/core/agents/` or `backend/core/ai/` → `BACKEND_AGENTS.md`
   - `frontend/src/features/` → `FRONTEND_FEATURES.md`
   - `frontend/src/store/` → `FRONTEND_STORE.md`
   - `frontend/src/shared/` → `FRONTEND_SHARED.md`

3. **Read each affected map** — check if changed files/components are documented. Look for:
   - Missing entries for new files
   - Outdated descriptions for modified files
   - Entries for deleted files that should be removed
   - New patterns or conventions not captured

4. **Report drift** — list what's missing or outdated per map before making changes.

5. **Apply targeted edits** — update only the sections affected. Do NOT regenerate from scratch. Preserve existing content and patch. Match the existing format (table rows, one-line descriptions).

6. **Update GLOSSARY.md** — add entries for any new concepts, patterns, or components.

7. **Update COMMANDS.md** — if new commands or workflows were added.

## Rules

- This is a **patch operation**, not a rebuild. Don't delete existing content that's still accurate.
- Keep entries concise — one line per file/module. Maps are indexes, not documentation.
- Run architecture map updates in parallel where possible (use Agent tool).
- Stage the updated maps for the user to review and commit.
