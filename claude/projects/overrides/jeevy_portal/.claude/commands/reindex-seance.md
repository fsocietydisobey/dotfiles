# /reindex-seance

Reindex Séance's semantic search index for this project. Uses the incremental mode — `git diff` aware, only re-embeds files changed since the last index. Fast.

## What to do

1. Call `mcp__seance__reindex_changed` with:
   - `path`: `/home/_3ntropy/work/jeevy_portal`
   - `name`: `jeevy_portal`

2. Report back:
   - Number of files reindexed
   - Chunk count delta
   - Any failures (per-file errors)

3. If the MCP tool call fails or isn't reachable, fall back to the shell CLI:
   ```bash
   tool mcp reindex jeevy-portal
   ```

## When to use

- After pulling new code or merging a branch
- Before starting a session where you'll rely on `semantic_search` against recent code
- If `semantic_search` keeps returning old code paths that no longer exist

## What NOT to do

- Don't run a full `index_project` unless the incremental reindex fails hard — a full reindex takes minutes and re-embeds everything. Incremental is correct for 99% of cases.
