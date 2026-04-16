---
description: Refresh the CLAUDE.md for every frontend feature folder
---

Run `/update-feature-claude-md` across **every** feature under `frontend/src/features/`. This is the bulk-refresh skill — use it after a large refactor when many features have drifted, not for everyday updates.

## When to use this skill

- **After a large refactor** that touched multiple features (e.g. moving `OverviewCard` to `shared/components/`, splitting a feature, renaming a barrel).
- **After a CLAUDE.md template change** — if the template adds a new section (like "Permissions" or "Common tasks"), this skill rolls it out everywhere.
- **As a periodic freshness check** — once a quarter or so, regenerate everything to catch silent drift in line counts, file moves, and consumer changes.

**Don't use this skill for everyday updates.** If a single feature changed, use `/update-feature-claude-md <name>` directly — it's faster and protects against accidentally rewriting files that didn't need it.

## Steps

1. **List all features.** Run `ls frontend/src/features/` and collect every directory (skip files like `README.md`).

2. **Group by complexity.** Small features (single component, ≤3 files) can be researched directly in the main context. Large features (15+ files, complex state) should be researched via Explore subagents to protect main context.

3. **Process small features directly.**
   - Read the feature's main files yourself.
   - Apply the template from `/update-feature-claude-md` (see that skill for the template).
   - Write the CLAUDE.md.
   - Format with Prettier.

4. **Process large features via Explore subagents in batches of 5.**
   - Fire 5 parallel `Explore` subagents, each researching one feature with this prompt structure:
     - One-liner, Vocabulary, Public API, Key files, Data and state, Conventions and patterns, Consumers, Known issues and gotchas, Relevant study guides.
   - Wait for all 5 to return.
   - Write 5 CLAUDE.mds in parallel from the summaries.
   - Format the batch with one Prettier call.
   - Repeat until all large features are covered.

5. **Preserve human-curated content** in any existing CLAUDE.md. See `/update-feature-claude-md` for the preserve-vs-regenerate rules. The same rules apply per-file; this skill is just the batch runner.

6. **Update the deep-imports tracker.** As you discover new cross-feature deep imports, add them to `shared-docs/tech-debt/DEEP_IMPORTS.md`. Don't let this drift across 22 separate files.

7. **Freshness markers.** Every file gets its `<!-- Last synced: YYYY-MM-DD -->` updated to today's date.

## Reporting

After the sync completes, return a concise summary:

```
## Sync complete

**Features refreshed:** 22
**Sections regenerated:** Architecture, Public API, Key files, Data, Consumers, See also
**Sections preserved:** Vocabulary, Common tasks, Known issues, Conventions

**New cross-feature deep imports added to DEEP_IMPORTS.md:**
- <feature> → <other-feature> (<file>)
- ...

**Notable changes since last sync:**
- <feature>: <summary of structural changes>
- ...

**Features that may need human review:**
- <feature>: <reason — e.g. existing structure diverged from template>
```

## What NOT to do

- **Don't run this skill for a single-feature change.** Use `/update-feature-claude-md <name>` instead.
- **Don't lose `**Why:**` lines.** The bulk preserve rules from `/update-feature-claude-md` apply here too.
- **Don't fire all 22 subagents at once.** Batches of 5 are the right size — too many parallel agents balloon main context with returned summaries.
- **Don't run Prettier 22 times.** Format files in batches via a single Prettier invocation per batch.
- **Don't skip the deep-imports tracker update.** That's the whole point of having it — feature CLAUDE.mds reference the tracker rather than carrying their own "fix if touched" wishes, so the tracker has to stay accurate during a sync.
