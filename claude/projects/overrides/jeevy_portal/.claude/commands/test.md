---
description: Write tests for the current file following this project's test patterns
---

Write tests for the file I'm working on (or the file I specify).

## Before you start

1. Read the target file completely — understand what it does, its public surface, and its dependencies.
2. Find existing tests in the project that cover similar code. Match their patterns:
   - Backend: look under `backend/tests/` for the mirrored path
   - Frontend: look for `*.test.ts` / `*.test.tsx` files next to the source
3. Read `.claude/rules/testing.md` for the project's test standards.

## What to cover

- **Happy path** — the primary use case with valid input
- **Edge cases** — empty inputs, null/undefined, boundary values, zero-length lists, unicode
- **Error paths** — invalid input, missing permissions, resource not found, downstream failures
- **Tenant isolation** (backend) — verify cross-tenant data is not accessible
- **Concurrency** (where relevant) — race conditions, double-submission, idempotency

## What NOT to test

- Framework behavior (React re-rendering on state change, FastAPI routing)
- Trivial pass-throughs and getters
- Implementation details that would tie the test to internal structure

## Patterns to follow

**Backend (pytest)**
- Use real PostgreSQL via test containers, not mocks for the DB layer
- Mock external services (Gemini, third-party APIs) at the boundary
- Use factories/fixtures for test data — no hardcoded magic values
- Async tests use `pytest-asyncio` with `@pytest.mark.asyncio`
- Group with descriptive `describe`-equivalent class names: `class TestProjectService:`

**Frontend (vitest / react-testing-library)**
- Test user-visible behavior, not component internals
- Use `screen.getByRole`, not `getByTestId`, where possible
- Mock RTK Query endpoints via `msw`, not by stubbing the hook directly
- Reset handlers between tests to prevent pollution

## Test naming

Descriptive sentences that read as specifications:
- ✅ `"returns empty list when user has no projects"`
- ✅ `"raises ValidationError when email is missing"`
- ❌ `"test1"`, `"works correctly"`, `"happy path"`

## Output

1. Create or update the appropriate test file (mirrored path).
2. Run the new tests to confirm they pass (and fail appropriately when the code is broken).
3. Summarize what you covered and what you deliberately left out.

If the target file is so tightly coupled that tests would be brittle, say so and propose a small refactor first — don't write fragile tests just to hit coverage.
