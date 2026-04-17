# /update-scarlet-docs

Audit Scarlet-generated feature documentation across this project, figure out what's stale, and regenerate what needs regenerating. Read-and-then-write — decisions happen based on actual lint + git evidence, not blanket regeneration.

## Workflow

### 1. Gather state

Run these in parallel:

- `mcp__scarlet__analyze_project(path="/home/_3ntropy/work/jeevy_portal")` — baseline framework/structure info
- `mcp__scarlet__scan_features(path="/home/_3ntropy/work/jeevy_portal")` — enumerate every feature with its current state (has_claude_md, has_barrel, counts)

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
deliverable-workspace    recent_changes      47 files changed, CLAUDE.md 3 weeks old
project-overview         missing_barrel      no index.js (flag only)
account                  clean               —
...
```

End with a count line: `N stale, M missing, K recent-changes, B missing-barrel, C clean`.

### 5. Regenerate what's stale (and create what's missing)

Two distinct write paths — treat them differently:

**Path A — `missing_doc` (CREATE from scratch)**

For every feature with no CLAUDE.md, call `build_claude_md` directly. There's no existing content to preserve.

```
mcp__scarlet__build_claude_md(
    project_path="/home/_3ntropy/work/jeevy_portal",
    feature_path=<feature.path>,
    write=True
)
```

The generated skeleton has placeholder manual sections the user can fill in later. Safe — no chance of destroying anything because nothing exists.

**Path B — `stale_exports` + `recent_changes` (UPDATE existing)**

For features with an existing CLAUDE.md, do a marker check first. Read the file and look for both `<!-- BEGIN MANUAL -->` and `<!-- END MANUAL -->`.

- **Markers present** → safe to regenerate. Call `build_claude_md(write=True)`. Auto-sections refresh; hand-written content between markers is preserved.
- **Markers missing** → the existing CLAUDE.md was hand-written (or predates Scarlet). DO NOT regenerate silently. Report this feature to the user with its path and ask whether to proceed. If they say yes, run `build_claude_md(write=True)` and note that manual content may be overwritten.

Run all eligible regenerations (Path A + approved Path B) in parallel.

### 6. Final report

Print:
- List of features actually regenerated (with tick marks)
- Any that failed (with error messages)
- `missing_barrel` features flagged but skipped, with the one-liner needed to fix them manually if desired:
  ```bash
  mcp__scarlet__generate_barrel(feature_path=..., write=True)
  ```

## What NOT to do

- **Don't regenerate barrels automatically.** Some features intentionally don't use a barrel. Flag and stop.
- **Don't regenerate the dep graph automatically.** That's a project-wide artifact; refresh it separately when you want to.
- **Don't blindly regenerate everything.** The whole point of this command is to be evidence-based — if the lint is clean and files haven't changed recently, leave the CLAUDE.md alone. Unnecessary rewrites waste time and create noise in git.
- **Don't proceed past step 5 without the `BEGIN MANUAL` marker check.** A regeneration without markers will destroy hand-written content.

## When to use

- After a significant refactor that may have moved or renamed exports
- After a merge of a long-running branch
- Weekly hygiene — catch drift before it accumulates
- Before generating a project architecture overview (dep graph, onboarding docs) — want the inputs fresh
