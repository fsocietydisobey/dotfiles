# Séance (semantic codebase search)

Séance is an MCP server that provides semantic search over indexed codebases. Use it for vague, conceptual queries — it understands meaning, not just keywords.

## When to use Séance vs grep

- **Séance:** "how does auth work?", "what handles retries?", "find code related to payment processing"
- **Grep:** exact symbol names, specific strings, known function/class names
- **Serena (jeevy_portal only):** "find all references to X", "who calls Y", LSP-powered navigation

## Workflow

1. Before searching a project with Séance, call `reindex_changed` if the user has been actively coding — keeps the index fresh.
2. Use `semantic_search` with natural language. Don't try to keyword-optimize the query — describe what you're looking for conceptually.
3. Read the top 2-3 results to build context, then read the actual source files for full understanding.
4. Use filters (`language`, `chunk_type`) when the user is looking for something specific (e.g., "find Python classes related to state management").

## Indexed projects

| Project | Name (for search) | Location |
|---|---|---|
| Jeevy Portal | `jeevy-portal` | `~/work/jeevy_portal` |
| Chimera | `chimera` | `~/dev/chimera` |
| AI Orchestrator | `ai-orchestrator` | `~/dev/ai-orchestrator` |
| Meeting Scribe | `meeting-scribe` | `~/dev/meeting-scribe` |
| Séance | `seance` | `~/dev/seance` |
| Telegram Review | `telegram-review` | `~/dev/telegram-review` |

## Quick reference

```
semantic_search(query, project, top_k=10, language=None, chunk_type=None)
index_project(path, name)
reindex_changed(path, name)
find_similar(project, file_path, symbol_name, top_k=5)
list_projects()
```
