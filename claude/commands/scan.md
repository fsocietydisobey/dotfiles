# /scan — Project structure scan

Scan the current project using Scarlet and report its structural state.

## Steps

1. Call `analyze_project` on the current working directory to detect framework, state management, test framework, and package manager.
2. Call `scan_features` to list all features with their state (CLAUDE.md, barrel exports, component/hook/slice counts).
3. Present a summary table showing:
   - Total features and how many have CLAUDE.md files
   - How many have barrel exports
   - Any features with high component counts that might need sub-grouping
4. If any features are missing CLAUDE.md or barrel exports, note them as candidates for `scarlet describe` or `scarlet barrel`.
