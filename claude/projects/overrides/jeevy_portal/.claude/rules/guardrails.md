# Guardrails

## Git restrictions

- **Don't run state-changing git commands** (commit, push, pull, checkout, switch, merge, rebase, reset, stash, cherry-pick, etc.). I handle all git operations manually.
- **Read-only git inspection is allowed** (`git show`, `git diff`, `git log`, `git ls-tree`) to look at code in other branches. Do not switch branches or modify the working tree.

## Don't

- Don't commit secrets or real API keys; use env vars and `.env` / `.env.local` (keep those out of version control).
- Don't break existing imports without updating all call sites or leaving a re-export where appropriate.
- Don't add large binary or generated blobs to the repo; use refs, fixtures, or external storage.
