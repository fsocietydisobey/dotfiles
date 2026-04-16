---
description: Generate or refresh the CLAUDE.md for a specific frontend feature folder
---

Generate (or refresh) the `CLAUDE.md` for a single feature under `frontend/src/features/<feature-name>/`. The user passes the feature name as the argument (e.g. `/update-feature-claude-md drawings`).

## What this skill produces

A single file at `frontend/src/features/<feature-name>/CLAUDE.md` following the validated template that all 22 features in this project use. The file is feature-scoped expert context that Claude Code auto-loads when editing files inside the feature folder.

## Steps

1. **Resolve the feature.** Confirm `frontend/src/features/<name>/` exists. If the feature has a `CLAUDE.md` already, **read it first** and preserve the human-curated parts (vocabulary, common tasks, gotchas with `**Why:**` lines that aren't trivially auto-derivable). The auto-derivable parts (file list, public API, consumers) get refreshed.

2. **Walk the feature folder.** Use `Glob` and `Read` to identify:
   - The barrel (`index.js`) and what it exports.
   - The top-level component files and their line counts.
   - Any subfolder structure (component folders, hooks/, utils/).
   - Cross-feature imports (`@/features/<other>/...`).

3. **Find consumers.** Run `Grep` for `@/features/<feature-name>` across `frontend/src/`. Categorize hits as:
   - **Barrel imports** (`from "@/features/<name>"`) — clean.
   - **Deep imports** (`from "@/features/<name>/components/..."` or similar) — tracked in `shared-docs/tech-debt/DEEP_IMPORTS.md`.

4. **Cross-reference study guides.** Walk `frontend/study-guides/{layout,tables,auth,styling}/` and identify which guides directly apply to this feature's specific patterns. Skip guides that only apply project-wide (those are referenced from `.claude/rules/frontend-*.md`, which is auto-loaded).

5. **Detect non-obvious patterns and gotchas.** Scan the feature's main files for:
   - Raw `fetch()` calls to legacy `/api/` proxy routes (deprecated — flag for migration to RTK Query via `fastApiBaseQuery`).
   - Mixed snake_case/camelCase reads (`x.foo_bar ?? x.fooBar` patterns).
   - Hardcoded magic numbers (timers, limits, thresholds).
   - `alert()` / `window.confirm()` vs `react-toastify` inconsistency.
   - Inline hex color values (violates `.claude/rules/frontend-styling.md`).
   - Cross-feature deep imports (both inbound and outbound).
   - Custom hooks, optimistic update patterns, debounced writes, mutually-exclusive state fields.

6. **Use the validated template** (see below).

7. **Write the file** to `frontend/src/features/<name>/CLAUDE.md`. Format with Prettier:
   ```bash
   PATH="/home/_3ntropy/.nvm/versions/node/v22.13.0/bin:$PATH" && cd /home/_3ntropy/work/jeevy_portal/frontend && npx prettier --write src/features/<name>/CLAUDE.md
   ```

8. **Update the freshness marker** at the bottom of the file to today's date.

9. **If you found new deep imports**, also update `shared-docs/tech-debt/DEEP_IMPORTS.md` to add them.

## Template

```markdown
# Feature: <Name>

<one-line description of what the feature does and where it fits in the app>

## Architecture

<Mermaid diagram showing internal hierarchy and cross-feature deps. Skip this
section entirely if the feature is a single component with no cross-feature
relationships — write a one-line note instead.>

## Vocabulary

<Domain terms a reader needs to know. Skip section if the feature has no
special vocabulary. Distinguish overloaded words explicitly.>

## Public API (import from `@/features/<name>`)

<What `index.js` exports. Format: `- <Name> — one-sentence purpose`.>

## Key files

<3-6 most important files with line count and one-sentence purpose. Focus on
files most likely to be edited.>

## Data and state

<RTK Query endpoints used, Redux slices, React Context, local state. Keep short.>

## Conventions and patterns

<Non-obvious conventions SPECIFIC to this feature. Each item should have a
**Why:** line explaining the rationale — rules without reasons rot into cargo
culting.>

## Permissions

<Permission gates that affect this feature. If none, say "None at the feature
layer (route-level access enforced upstream)".>

## Common tasks

<2-3 numbered recipes for common modifications. Each recipe should be runnable
end-to-end without consulting other docs. For wrapper/trivial features, mark
as "N/A" and explain why.>

## Consumers

<Who imports from this feature. Format:
- Via barrel: list with arrow notation
- Via deep imports: list with reference to shared-docs/tech-debt/DEEP_IMPORTS.md
>

## Known issues and gotchas

<Each gotcha must include a **Why:** line. If the why is unknown, say so
explicitly: "the comment doesn't say — check git blame". Don't fabricate.>

## See also (study guides)

<Direct links to relevant frontend/study-guides/ files. Skip generic ones
covered by .claude/rules/frontend-*.md.>

<!-- Last synced: YYYY-MM-DD -->
<!-- Regenerate: /update-feature-claude-md <name> -->
```

## What to preserve from an existing CLAUDE.md

When refreshing, **preserve** these sections (they contain human judgment that the skill cannot regenerate):

- **Vocabulary** — domain terms with their definitions.
- **Common tasks** — recipes the user has refined.
- **Known issues and gotchas** — especially `**Why:**` lines that came from incident knowledge or `git blame`.
- **Conventions and patterns** — the rationale for non-obvious choices.

**Regenerate** these sections fresh:

- **Architecture** Mermaid diagram (the file structure may have changed).
- **Public API** (re-derived from `index.js`).
- **Key files** (re-derived from folder walk + line counts).
- **Data and state** (re-derived from imports).
- **Consumers** (re-derived from grep).
- **See also** study guides (re-derived from name matching).

If the existing file's structure diverges from the template, **preserve the structure but warn the user** in the response so they can decide whether to manually align it.

## What NOT to do

- **Don't fabricate gotchas.** If a "Why:" is unknown, say "the code doesn't comment why — check git blame".
- **Don't generate a Mermaid diagram for trivial features.** A single-component feature with no cross-feature deps gets a one-line note.
- **Don't remove `**Why:**` lines** when refreshing. Those are the highest-value parts of the doc.
- **Don't fire subagents in this skill.** This is a single-feature operation; do the research yourself in the main context. (For batch refreshes use `/sync-all-feature-claude-md` instead.)
- **Don't forget the freshness marker.** Update both the date and the regenerate command at the bottom.

## After writing

Report what changed: which sections were preserved, which were regenerated, and any new gotchas or deep imports you flagged. If you added new entries to `shared-docs/tech-debt/DEEP_IMPORTS.md`, mention them.
