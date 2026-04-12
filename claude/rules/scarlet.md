# Scarlet (codebase cartography)

Scarlet is an MCP server that walks any project, extracts structural metadata via tree-sitter, and generates documentation scaffolding: per-feature CLAUDE.md files, barrel exports, dependency graphs, and lint reports.

## When to use Scarlet

- **Onboarding a new feature:** `scan_features` to see what's there, `extract_feature_metadata` to pull exports, `build_claude_md` to generate a skeleton.
- **After refactoring:** `lint_claude_md` to check if CLAUDE.md files are stale.
- **Architecture visibility:** `generate_dep_graph` to see feature → feature dependencies.
- **Finding gotchas:** `extract_invariants` to surface warning comments, magic numbers, and TODOs.

## Quick reference

```
analyze_project(path)
scan_features(path)
extract_feature_metadata(feature_path)
generate_barrel(feature_path, extension="js", write=True)
build_claude_md(project_path, feature_path, import_alias=None, write=True)
generate_dep_graph(path, format="mermaid")
lint_claude_md(feature_path)
extract_invariants(feature_path)
list_consumers(project_path, feature_name)
```
