---
description: What to test, coverage philosophy, determinism, structure
paths:
  - "**/*.test.{ts,tsx,js,jsx,py}"
  - "**/*.spec.{ts,tsx,js,jsx,py}"
  - "**/tests/**"
  - "**/__tests__/**"
  - "**/test_*.py"
  - "**/conftest.py"
  - "**/spec/**"
---

# Testing

## Philosophy

- Tests exist to **catch regressions and document behavior.** If a test doesn't fail when something breaks, it's not testing anything useful.
- Test **behavior, not implementation.** Test what a function returns or what side effects it produces — not how it does it internally. Implementation can change; contracts shouldn't.
- Every bug fix should add a test that would have caught the bug. Bugs are evidence of missing test coverage.

## What to test

- **Critical paths:** Authentication, data mutations, payment flows, core business logic. These get thorough coverage.
- **Edge cases:** Empty inputs, null/undefined, boundary values, concurrent operations, error responses.
- **Integration points:** API endpoints, database queries, third-party service calls. These are where things actually break.

## What not to over-test

- Don't test framework behavior. If React renders a component when state changes, you don't need a test for that.
- Don't test trivial getters/setters or pure pass-through functions.
- Don't write tests that just assert the implementation you already wrote. The test should be derivable from the requirements, not the code.

## Structure

- Test files should mirror the source structure. `src/services/auth.js` → `tests/services/auth.test.js`.
- One describe block per function or component. Nested describes for different scenarios.
- Test names should read as specifications: `"returns empty array when user has no projects"`, not `"test1"` or `"works correctly"`.

## Determinism

- Tests must be deterministic. No reliance on wall-clock time, network state, or test execution order.
- Mock external services and I/O at the boundary — but prefer integration tests with real databases over mocking the DB layer when feasible.
- No flaky tests. If a test fails intermittently, fix it or delete it. Flaky tests erode trust in the suite.

## Coverage

- Aim for high coverage on critical paths (90%+). Don't chase 100% overall — diminishing returns.
- Coverage is a floor, not a ceiling. High coverage with weak assertions is worse than moderate coverage with meaningful tests.
