---
description: Format-as-you-go discipline and research-first workflow for non-trivial tasks
---

# Workflow

## Formatting as you go

- **Format every file you modify** — don't wait for commit time.
- Frontend: Prettier
- Backend: Black
- Run the formatter immediately after making changes.

## Research-first workflow

The preferred workflow for any non-trivial task:

1. **Research the codebase** — read the actual source files, trace data flows, understand current behavior.
2. **Fact-check with documentation** — verify library/framework behavior against official docs.
3. **Plan with detail** — task specs and implementation plans should be thorough enough for someone unfamiliar with the codebase.
4. **Implement step by step** — follow the plan, check off items, update the plan when reality diverges.
5. **Verify** — run tests, check edge cases, format code.
