# /search — Semantic codebase search

Search the indexed codebases using Séance. Pass a natural language query as the argument.

## Usage

`/search how does authentication work`
`/search payment processing flow`
`/search error handling patterns`

## Steps

1. Determine which project to search. If the current working directory is inside a known project, use that. Otherwise, ask the user.
2. Call `reindex_changed` on the project path to ensure the index is fresh.
3. Call `semantic_search` with the user's query and the project name. Use `top_k=10`.
4. Read the top 2-3 result files to build full context.
5. Summarize what was found: which files are relevant, how they connect, and answer the user's question.
