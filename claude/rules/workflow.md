# Workflow & Sync

## Rule file sync (CRITICAL)

**`~/.claude/rules/` and `~/.cursor/rules/` must always be in sync.** These are the same personal rules for different AI tools. When you add, change, or remove a rule in one location, immediately update the other to match.

The content is semantically identical — only the format differs:
- Claude: plain `.md` files
- Cursor: `.mdc` files with YAML frontmatter (`description`, `alwaysApply: true`)

## Formatting as you go

- **Format every file you modify** — don't wait for commit time.
- Frontend: Prettier
- Backend: Black
- Both tools should format immediately after making changes.

## Research-first workflow

The user's preferred workflow for any non-trivial task:

1. **Research the codebase** — read the actual source files, trace data flows, understand current behavior.
2. **Fact-check with documentation** — verify library/framework behavior against official docs.
3. **Plan with detail** — task specs and implementation plans should be thorough enough for someone unfamiliar with the codebase.
4. **Implement step by step** — follow the plan, check off items, update the plan when reality diverges.
5. **Verify** — run tests, check edge cases, format code.

## Continuous evolution

These rules represent the user's engineering thought process. They are a living system that improves over time:

- When the user corrects an approach → update the relevant rule to capture that learning.
- When the user confirms a non-obvious choice → note it so the pattern is repeated.
- When a rule produces bad results → revise or remove it.
- When a new pattern emerges across projects → add a rule for it.

The goal is convergence: over time, these rules should increasingly predict what the user would decide, so the AI operates as a natural extension of their thinking.
