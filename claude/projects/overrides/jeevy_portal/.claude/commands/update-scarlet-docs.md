# /update-scarlet-docs

Audit Scarlet-generated feature documentation, categorize what's stale, and regenerate what needs regenerating. Handles rich CLAUDE.md structures with project-specific sections (Architecture, Data and state, Permissions, etc.) — not just Scarlet's default template.

## Workflow

### 1. Gather state

Run these in parallel:

- `mcp__scarlet__analyze_project(path="/home/_3ntropy/work/jeevy_portal")` — baseline framework/structure info
- `mcp__scarlet__scan_features(path="/home/_3ntropy/work/jeevy_portal")` — enumerate every feature with its current state

### 2. Find what's stale

For each feature that has a CLAUDE.md, call `mcp__scarlet__lint_claude_md(feature_path=<feature.path>)` **in parallel** (one call per feature). Collect all reports.

Separately, determine recently-touched features:

```bash
git -C /home/_3ntropy/work/jeevy_portal log --since='2 weeks ago' --name-only --pretty=format: | sort -u
```

Map each changed file path back to its feature directory (files under `frontend/src/features/<name>/` belong to feature `<name>`).

### 3. Categorize findings

Bucket every feature into exactly one of:

| Category | Criterion |
|---|---|
| **stale_exports** | `lint_claude_md` reports exports in the CLAUDE.md that no longer exist, or current exports missing from CLAUDE.md |
| **missing_doc** | Feature exists in `scan_features` output but `has_claude_md: false` |
| **recent_changes** | Feature has files changed in last 2 weeks AND its CLAUDE.md last-modified timestamp is older than those changes |
| **missing_barrel** | Feature has CLAUDE.md but `has_barrel: false` — flag only, don't auto-fix |
| **clean** | No lint issues, CLAUDE.md exists, no recent drift |

### 4. Report findings

Print a concise summary table:

```
Feature                  Category            Reason
─────────────────────────────────────────────────────────────────────
drawings                 stale_exports       3 exports removed since last gen
...
```

End with a count line and present three options:

1. **Skip regeneration** — fix broken refs manually in place (option 3)
2. **Smart regenerate** (recommended, default) — auto-wrap markers, regenerate, splice custom sections back
3. **Force regenerate** (unsafe) — regenerate without preserving anything beyond Scarlet's known manual slots

Wait for the user's choice.

---

## Option 2 (Smart regenerate) — full workflow

When the user picks option 2, execute this entire workflow autonomously for every feature in `stale_exports`, `missing_doc`, and `recent_changes`. Do not stop to ask between features unless something unrecoverable happens.

### Step A: Section-map each feature's existing CLAUDE.md

For each feature with an existing CLAUDE.md, read it and split on `##` H2 headers. For each section, assign one of:

| Bucket | Match rule (case-insensitive, fuzzy) | What happens to it |
|---|---|---|
| **auto** | `Public API`, `Key files`, `Consumers`, `See also` | Scarlet regenerates this — skip in marker step |
| **scarlet-manual** | `Vocabulary`, `Conventions` or `Conventions and patterns`, `Common tasks`, `Gotchas` or `Known issues` or `Known issues and gotchas` | Wrap in `<!-- BEGIN MANUAL: <key> -->` with the appropriate key (see mapping below) |
| **description** | Any prose before the first H2 | Wrap as `<!-- BEGIN MANUAL: description -->` |
| **custom** | Anything else (Architecture, Data and state, Permissions, Invariants, etc.) | Record content + position; splice back post-regenerate |

Key mapping for scarlet-manual sections:

| Section header (any variant) | Key |
|---|---|
| Vocabulary | `vocabulary` |
| Conventions, Conventions and patterns | `conventions` |
| Common tasks | `common_tasks` |
| Gotchas, Known issues, Known issues and gotchas | `gotchas` |

### Step B: Wrap scarlet-manual sections with markers (if not already)

If the existing CLAUDE.md doesn't already have `<!-- BEGIN MANUAL: <key> -->` markers, insert them around each scarlet-manual section's body (between the `## Heading` line and the next `##`).

Example — before:
```markdown
## Vocabulary
- **CREATION_STEP** — enum for...
- **APP_MODE** — context selector...
```

After:
```markdown
## Vocabulary
<!-- BEGIN MANUAL: vocabulary -->
- **CREATION_STEP** — enum for...
- **APP_MODE** — context selector...
<!-- END MANUAL: vocabulary -->
```

Same pattern for `conventions`, `common_tasks`, `gotchas`, and the description (wrap the prose between the H1 title and the first H2).

Write the wrapped file back — this is a mechanical edit, not a regenerate yet.

### Step C: Record custom sections before regenerate

Before calling `build_claude_md`, capture each custom section:

```
custom_sections = [
  {
    "heading": "## Architecture",
    "body": "...full content including any mermaid diagrams, prose, images...",
    "anchor_before": "## Public API",   # the next section after it in the old file
    "anchor_after": "## Vocabulary",    # the section before it in the old file
  },
  ...
]
```

The `anchor_before` / `anchor_after` let you splice it back in roughly the same relative position after regenerate, even if Scarlet's template reorders things.

### Step D: Regenerate via Scarlet

Call:

```
mcp__scarlet__build_claude_md(
    project_path="/home/_3ntropy/work/jeevy_portal",
    feature_path=<feature.path>,
    write=True
)
```

Scarlet refreshes auto sections (Public API, Key files, Consumers, See also) and preserves the scarlet-manual sections via the markers we added in step B.

### Step E: Splice custom sections back into the new file

Read the newly regenerated CLAUDE.md. For each recorded `custom_sections` entry:

1. Find the `anchor_before` section header in the new file
2. Insert the custom section immediately before it (with `\n\n` separator)
3. If `anchor_before` doesn't exist in the new file (rare — possible if Scarlet dropped a section), fall back to `anchor_after`; if that's also absent, append at the end before any trailing HTML comments

Use the Edit tool with the exact heading + body captured in step C to inject the content.

### Step F: Verify nothing was lost

After splicing, verify:

1. Count H2 headers in old file vs new file — should match (except intentional drops if Scarlet renamed, e.g., "Permissions" stays if preserved)
2. Grep the new file for a distinctive substring from each custom section's body — confirm it's present
3. Report per-feature:
   - `[ok] drawings — refreshed 4 auto-sections, preserved 2 scarlet-manual + 3 custom sections`
   - `[warn] project-overview — custom section "Architecture" missing in new file` (if splice failed)

If any `[warn]` appears, stop and report — do not proceed to the next feature.

### Step G: Final report

Print a summary table: features regenerated cleanly, features with warnings, features skipped (`missing_barrel` flagged separately).

For `missing_barrel` features, emit the one-liner to fix manually if desired:

```
mcp__scarlet__generate_barrel(feature_path=..., write=True)
```

---

## Option 1 — Skip regeneration

Just walk each stale feature's CLAUDE.md and patch broken file references inline (using Edit for each broken-ref lint issue). Don't touch auto-sections. Report what was fixed. Leave `recent_changes` features alone since surface-level edits won't refresh their auto content.

## Option 3 — Force regenerate (only on explicit request)

Call `build_claude_md(write=True)` without the marker-wrapping or splice-back steps. Accept that any content Scarlet doesn't know about will be lost. Warn the user clearly what's being discarded before executing.

---

## Edge cases to handle

- **H2 headers inside code blocks**: ignore (parse markdown properly — don't split `## heading` that's inside ``` ``` fences)
- **Mermaid diagrams in custom sections**: preserve verbatim — they're valid markdown and shouldn't be reformatted
- **Trailing HTML comments** (e.g., `<!-- Last synced: 2026-04-11 -->`): let Scarlet's template overwrite the trailing-sync comment, but don't treat them as custom sections
- **A feature whose CLAUDE.md is fundamentally unconventional** (e.g., free-form prose with no H2 structure): skip it with a warning — "can't map sections, use option 1 or 3"

## What NOT to do

- **Don't regenerate without section analysis.** Always parse the existing CLAUDE.md first.
- **Don't lose custom content silently.** Always verify (step F) and warn.
- **Don't auto-regenerate barrels or the dep graph** — those are separate artifacts.
- **Don't batch all the writes across all features before verifying one.** Do one feature end-to-end (B→C→D→E→F), verify, then proceed. If feature N fails, you stop with a partial-update state that's still coherent.
