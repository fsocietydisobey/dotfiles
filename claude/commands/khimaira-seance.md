# /khimaira-seance — semantic codebase search via Séance

Use the Séance tool family (`mcp__khimaira__seance_*`) to answer a conceptual question about the current project. Séance reaches what `grep` can't — describe what you're looking for in plain English, get back the relevant chunks even when you don't know the exact symbol names.

## Steps

1. **Resolve the project name.** Use the cwd's directory name as a default (e.g. `khimaira` for `~/dev/khimaira`). Adjust if the user names a different project in `$ARGUMENTS`.
2. **Confirm the project is indexed.** Call `mcp__khimaira__seance_list_projects` once. If the project isn't in the list:
   - Tell the user it needs indexing first
   - Offer to run `mcp__khimaira__seance_index_project(path=<cwd>, name=<project>)` (takes 30s-2min for a typical codebase)
   - Wait for confirmation before indexing
3. **Search.** Call `mcp__khimaira__seance_semantic_search(query=$ARGUMENTS, project=<name>, top_k=10)`.
4. **Read the top 2-3 hits** with the standard `Read` tool to build context — the search returns chunk metadata, not full file contents.
5. **Synthesize.** Answer the user's actual question using what you found. Cite file paths + line ranges.

## When to use other tools instead

- **Exact symbol / known string** → just `Grep`. Séance is for *meaning*, not pattern matching.
- **"Find similar to this function"** → `mcp__khimaira__seance_find_similar(project, file, symbol)` is purpose-built for that.
- **No matches in Séance?** Re-phrase the query more abstractly. Embeddings are sensitive to framing. If two rephrasings turn up nothing, fall through to grep.

## Notes

- Séance indexes Python, TypeScript, JavaScript via tree-sitter. Other languages return no results.
- The search is local + offline once the index exists. No external API call per query.
- This command does NOT generate prose summaries of the codebase — it surfaces relevant code; you synthesize.
