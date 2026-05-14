# /khimaira-scarlet — codebase cartography via Scarlet

Use the Scarlet tool family (`mcp__khimaira__scarlet_*`) to map, document, or analyze the *structure* of a feature-organized codebase. Scarlet generates structure (exports, dep graphs, barrel files, CLAUDE.md skeletons) by walking the AST with tree-sitter; you generate the meaning (Vocabulary, Conventions, Gotchas) by reading what it surfaces.

## Steps

1. **Resolve the target path.** Use cwd as default, or the path in `$ARGUMENTS` if the user names a specific project / feature.
2. **Pick the right Scarlet tool for the intent in `$ARGUMENTS`:**

   - *"what does this project look like / scan features"* → `scarlet_analyze_project(path)` + `scarlet_scan_features(path)`
   - *"what does this feature export / its shape"* → `scarlet_extract_feature_metadata(feature_path)`
   - *"who depends on this / call sites"* → `scarlet_list_consumers(feature_path)`
   - *"generate a dep graph"* → `scarlet_generate_dep_graph(path, format='mermaid')`
   - *"generate / refresh CLAUDE.md for this feature"* → `scarlet_build_claude_md(project_root, feature_path)` (preserves `<!-- BEGIN MANUAL --> ... <!-- END MANUAL -->` sections)
   - *"generate barrel exports / index.js"* → `scarlet_generate_barrel(feature_path)`
   - *"find stale CLAUDE.md / lint docs"* → `scarlet_lint_claude_md(feature_path)`
   - *"surface invariants / TODO / magic numbers"* → `scarlet_extract_invariants(feature_path)`
3. **After Scarlet generates structure, fill in the meaning.** If you generated a CLAUDE.md skeleton, read the code in the feature and write the Vocabulary / Conventions / Common tasks / Gotchas sections by hand. Don't auto-generate prose; that's where Claude judgment goes.

## Skip when

The codebase isn't feature-organized (no `features/` folder convention). Scarlet returns `[]` cleanly but you've wasted the call. Plain Python libraries, monorepos with package-per-feature layouts, and most backend services don't fit. Most React / Next.js feature-folder projects do.

## Notes

- Scarlet runs `tree-sitter` parsers — Python, TypeScript, JavaScript supported. Other languages get empty metadata.
- Re-running `build_claude_md` on an existing CLAUDE.md is safe: auto-derivable sections refresh, manual sections preserve.
- For *concept* searches over the codebase (not structural), use `/khimaira-seance` instead. Scarlet doesn't understand what code means, only how it's organized.
